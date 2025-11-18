import os
import hashlib
import logging
from operator import itemgetter
from typing import Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser

from pipeline.models import AnalysisReport, FinalReport
from pipeline.utils import format_transcript, validate_transcript, validate_report_quality

logger = logging.getLogger(__name__)

class InterviewAnalysisPipeline:
    """
    Production-ready pipeline for analyzing interview transcripts.
    
    Features:
    - Two-stage analysis (Analyst → Synthesis)
    - Automatic error handling with retries
    - Result caching to save API costs
    - Input and output validation
    - Comprehensive logging
    
    Usage:
        pipeline = InterviewAnalysisPipeline(api_key="your_key")
        report = pipeline.analyze(transcript_dict)
    """
    
    def __init__(
        self, 
        api_key: str,
        model: str = "gemini-2.5-flash",
        enable_cache: bool = True,
        max_retries: int = 3
    ):
        api_key = os.getenv("GEMINI_API_KEY")
        self.api_key = api_key
        self.model = model
        self.enable_cache = enable_cache
        self.max_retries = max_retries
        self.cache = {} if enable_cache else None
        
        logger.info(f"Initializing pipeline with model: {model}")
        
        self._init_llms()
        self._setup_chains()
        
        logger.info("✓ Pipeline initialized successfully")
    
    def _init_llms(self):
        try:
            self.analyst_llm = ChatGoogleGenerativeAI(
                model=self.model, temperature=0.0, google_api_key=self.api_key
            )
            self.synthesis_llm = ChatGoogleGenerativeAI(
                model=self.model, temperature=0.5, google_api_key=self.api_key
            )
            logger.info("✓ LLMs initialized")
        except Exception as e:
            logger.error(f"Failed to initialize LLMs: {e}")
            raise
    
    def _setup_chains(self):
        try:
            self.analyst_parser = PydanticOutputParser(pydantic_object=AnalysisReport)
            self.analyst_fixing_parser = OutputFixingParser.from_llm(
                parser=self.analyst_parser,
                llm=self.analyst_llm
            )
            analyst_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a meticulous, unbiased interview analyst. Your sole job is to read the following interview transcript and extract key performance snippets.

You must not judge or synthesize the overall performance. Only extract factual, self-contained observations.

Rules:
1. Extract 3-7 snippets
2. Each snippet must be objective and factual
3. Each snippet must include the EXACT quote from transcript
4. Tag each snippet: 'strength', 'weakness', or 'neutral'
5. No overall judgments - just observations

{format_instructions}"""),
                ("human", "Interview Transcript:\n{transcript}")
            ])
            self.analyst_chain = (
                {
                    "transcript": itemgetter("transcript"),
                    "format_instructions": lambda _: self.analyst_parser.get_format_instructions()
                }
                | analyst_prompt
                | self.analyst_llm
                | self.analyst_fixing_parser
            )
            self.final_parser = PydanticOutputParser(pydantic_object=FinalReport)
            self.final_fixing_parser = OutputFixingParser.from_llm(
                parser=self.final_parser,
                llm=self.synthesis_llm
            )
            synthesis_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a world-class Senior Engineering Manager and empathetic mentor. You have been given a factual, pre-analyzed report from an analyst about an intern candidate.

Your task: Generate a comprehensive, actionable report.

Process:
1. Summarize the candidate in 2-3 sentences (headline + impression)
2. Identify 2-3 key strengths with evidence
3. Identify 2-3 key weaknesses with evidence  
4. Create a prioritized 2-week development roadmap (5-7 steps)
5. Recommend 3-5 high-quality learning resources

Tone: Professional but encouraging. Focus on growth.

{format_instructions}"""),
                ("human", "Analyst Report:\n{analysis_report}")
            ])
            self.synthesis_chain = (
                {
                    "analysis_report": itemgetter("analysis_report"),
                    "format_instructions": lambda _: self.final_parser.get_format_instructions()
                }
                | synthesis_prompt
                | self.synthesis_llm
                | self.final_fixing_parser
            )
            logger.info("✓ Chains configured")
        except Exception as e:
            logger.error(f"Failed to setup chains: {e}")
            raise
    
    def _get_cache_key(self, transcript: str) -> str:
        return hashlib.md5(transcript.encode()).hexdigest()
    
    def _invoke_with_retry(self, chain, input_data: dict, stage_name: str):
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"[{stage_name}] Attempt {attempt}/{self.max_retries}")
                result = chain.invoke(input_data)
                logger.info(f"[{stage_name}] ✓ Success")
                return result
            except Exception as e:
                logger.warning(f"[{stage_name}] Attempt {attempt} failed: {e}")
                if attempt == self.max_retries:
                    logger.error(f"[{stage_name}] All attempts failed")
                    raise
                logger.info(f"[{stage_name}] Retrying...")
    
    def analyze(
        self, 
        transcript: Dict[str, str],
        validate_input: bool = True,
        validate_output: bool = True,
        use_cache: bool = True
    ) -> FinalReport:
        logger.info("="*60)
        logger.info("Starting Interview Analysis Pipeline")
        logger.info("="*60)
        if validate_input:
            logger.info("Validating transcript...")
            is_valid, error_msg = validate_transcript(transcript)
            if not is_valid:
                logger.error(f"Validation failed: {error_msg}")
                raise ValueError(f"Invalid transcript: {error_msg}")
            logger.info("✓ Transcript is valid")
        formatted_transcript = format_transcript(transcript)
        logger.info(f"✓ Transcript formatted ({len(formatted_transcript)} chars)")
        if use_cache and self.enable_cache:
            cache_key = self._get_cache_key(formatted_transcript)
            if cache_key in self.cache:
                logger.info("✓ Cache hit! Returning cached result")
                return self.cache[cache_key]
            logger.info("Cache miss, proceeding with analysis")
        logger.info("Stage 1: Running Analyst Agent...")
        analysis_report = self._invoke_with_retry(
            self.analyst_chain,
            {"transcript": formatted_transcript},
            "Analyst"
        )
        logger.info(f"✓ Analysis complete: {len(analysis_report.snippets)} snippets extracted")
        logger.info("Stage 2: Running Synthesis Agent...")
        final_report = self._invoke_with_retry(
            self.synthesis_chain,
            {"analysis_report": analysis_report.model_dump_json(indent=2)},
            "Synthesis"
        )
        logger.info("✓ Synthesis complete")
        if validate_output:
            logger.info("Validating report quality...")
            is_valid, issues = validate_report_quality(final_report)
            if not is_valid:
                logger.warning(f"Report quality issues detected:")
                for issue in issues:
                    logger.warning(f"  - {issue}")
            else:
                logger.info("✓ Report quality validated")
        if use_cache and self.enable_cache:
            cache_key = self._get_cache_key(formatted_transcript)
            self.cache[cache_key] = final_report
            logger.info("✓ Result cached")
        logger.info("="*60)
        logger.info("Pipeline Completed Successfully!")
        logger.info("="*60)
        return final_report
    
    def clear_cache(self):
        if self.cache:
            self.cache.clear()
            logger.info("✓ Cache cleared")
    
    def get_cache_stats(self) -> dict:
        if not self.enable_cache:
            return {"enabled": False}
        return {
            "enabled": True,
            "size": len(self.cache),
            "keys": list(self.cache.keys())
        }

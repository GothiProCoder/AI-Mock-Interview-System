import pytest
from pipeline.pipeline import InterviewAnalysisPipeline

mock_transcript = {
  "metadata": {
    "candidate_id": "C-EDGE-01",
    "position": "Backend Engineer Intern"
  },
  "transcript": {
    "interviewer": "Thanks for your time today. Let's start with a database question. Can you explain the difference between SQL and NoSQL databases?",
    "candidate": "Yeah, for sure. SQL is for, like, structured data, you know, tables and rows. NoSQL is for everything else, basically unstructured stuff. It's newer and generally faster.",
    "interviewer_1": "Okay, could you give an example of when you might prefer a NoSQL database like MongoDB over a SQL database like PostgreSQL?",
    "candidate_1": "Definitely. You'd use Mongo for something like a social media feed, where you have posts and comments. It's schema-less, so you can just dump any JSON in there. It's much more flexible.",
    "interviewer_2": "That's a good example. Now, let's talk about ACID properties. Can you tell me what 'C' stands for?",
    "candidate_2": "C stands for 'Concurrency'. It means the database can handle many transactions at once.",
    "interviewer_3": "Are you sure about that? Take a moment to think about the other letters: Atomicity, Isolation, Durability.",
    "candidate_3": "Oh, right, my mistake. I got confused. 'C' stands for 'Consistency'. It ensures that any transaction will bring the database from one valid state to another. Concurrency is more related to the 'Isolation' property. Thanks for the correction.",
    "interviewer_4": "No problem. Let's move on. Tell me about a time you faced a major challenge on a project.",
    "candidate_4": "Wow, yeah, so on this one school project, we had to build this web app. My teammates were not really pulling their weight, to be honest. I had to basically do the whole backend myself. I chose to use Python with Flask because I was comfortable with it, and for the database, I just used SQLite because it was easy. It was a huge challenge because the deadline was super tight, and I remember one night I was up until 3 AM trying to figure out this one bug with the user login. It turned out I had a typo in an environment variable. It was super stressful, but I got it done and we passed the class. I learned a lot about time management."
  }
}

def test_pipeline_init():
    pipeline = InterviewAnalysisPipeline(api_key="test_key", enable_cache=False)
    assert pipeline is not None

def test_analyze_valid():
    pipeline = InterviewAnalysisPipeline(api_key="test_key", enable_cache=False, max_retries=1)
    report = pipeline.analyze(mock_transcript, validate_input=True, validate_output=False)
    assert report is not None
    assert hasattr(report, "candidate_summary")
    assert hasattr(report, "insights")

def test_analyze_invalid_input():
    pipeline = InterviewAnalysisPipeline(api_key="test_key", enable_cache=False)
    with pytest.raises(ValueError):
        pipeline.analyze({}, validate_input=True)

def test_caching_behavior():
    pipeline = InterviewAnalysisPipeline(api_key="test_key", enable_cache=True)
    pipeline.clear_cache()
    report1 = pipeline.analyze(mock_transcript)
    report2 = pipeline.analyze(mock_transcript)
    assert report1 == report2

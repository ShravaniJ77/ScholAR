"""Quick validation script to test all modules."""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test all imports."""
    try:
        logger.info("Testing imports...")

        import config
        logger.info("✓ config")

        import models
        logger.info("✓ models")

        import semantic_scholar
        logger.info("✓ semantic_scholar")

        import llm_client
        logger.info("✓ llm_client")

        import research_agent
        logger.info("✓ research_agent")

        import report_generator
        logger.info("✓ report_generator")

        logger.info("✅ All imports successful!")
        return True

    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_connectivity():
    """Test API connectivity."""
    try:
        logger.info("\nTesting API connectivity...")

        from semantic_scholar import SemanticScholarClient
        client = SemanticScholarClient()

        logger.info("Testing Semantic Scholar API...")
        papers = client.search_papers("neural networks", limit=2)
        logger.info(f"✓ Semantic Scholar API working ({len(papers)} papers found)")
        client.close()

        return True

    except Exception as e:
        logger.error(f"❌ API test failed: {e}")
        return False


def test_llm_connectivity():
    """Test LLM connectivity."""
    try:
        logger.info("\nTesting LLM connectivity...")

        from llm_client import OpenRouterClient
        llm = OpenRouterClient()

        logger.info("Testing OpenRouter LLM...")
        result = llm.call_model("Say 'Hello from ScholAR' in one word.", max_tokens=10)

        if result:
            logger.info(f"✓ OpenRouter LLM working (Response: {result})")
            return True
        else:
            logger.error("❌ LLM returned no response")
            return False

    except Exception as e:
        logger.error(f"❌ LLM test failed: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*50)
    print("ScholAR System Validation")
    print("="*50 + "\n")

    results = []

    # Test imports
    results.append(("Imports", test_imports()))

    # Test APIs
    results.append(("Semantic Scholar API", test_api_connectivity()))
    results.append(("OpenRouter LLM", test_llm_connectivity()))

    # Summary
    print("\n" + "="*50)
    print("Validation Summary")
    print("="*50)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")

    all_passed = all(passed for _, passed in results)

    if all_passed:
        print("\n🎉 All tests passed! System is ready.")
        print("\nTo start the Streamlit app, run:")
        print("  streamlit run streamlit_app.py")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")

    sys.exit(0 if all_passed else 1)

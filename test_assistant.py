from ai_assistant import AIAssistant
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ai_assistant():
    assistant = AIAssistant(num_layers=2, agents_per_layer=2, tot_depth=2, tot_branching=2)
    
    test_inputs = [
        "What is the capital of France?",
        "Count from 1 to 5.",
        "Explain the concept of artificial intelligence in simple terms.",
        "In the UK, I am fitting the electrics for a 3 bedroom semi-detached house. Please provide a breakdown of the cost of materials and labour based on cost-effectiveness and energy efficiency that we will require to ensure that the house is fully functional."
    ]
    
    for input_text in test_inputs:
        logger.info(f"\nTesting input: {input_text}")
        
        for concise in [True, False]:
            start_time = time.time()
            
            try:
                response = assistant.respond(input_text, concise=concise)
                end_time = time.time()
                
                logger.info(f"{'Concise' if concise else 'Comprehensive'} Response:")
                logger.info(response)
                logger.info(f"Time taken: {end_time - start_time:.2f} seconds")
            
            except Exception as e:
                logger.error(f"Error occurred while processing input '{input_text}': {str(e)}")
            
            time.sleep(5)  # Add a delay between tests to avoid rate limiting

if __name__ == "__main__":
    test_ai_assistant()
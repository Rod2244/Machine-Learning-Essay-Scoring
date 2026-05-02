"""
Test script for the improved semantic topic relevance detection
"""

def test_topic_relevance():
    """Test various essay-topic combinations"""
    
    from topic_relevance_service import get_topic_relevance_service
    
    service = get_topic_relevance_service()
    
    test_cases = [
        {
            "name": "Perfect on-topic essay",
            "prompt": "Discuss the impact of climate change on polar bears",
            "essay": "Climate change has devastating effects on polar bears. Rising temperatures melt Arctic ice, their natural habitat. Bears struggle to find food as seal populations shift. Global warming accelerates ice loss, forcing polar bears to migrate and adapt. The species faces extinction without urgent climate action."
        },
        {
            "name": "Partially off-topic essay",
            "prompt": "Discuss the impact of climate change on polar bears",
            "essay": "Environmental issues are important. Polar bears are large animals. Climate is always changing. We should care about nature. Global warming affects weather patterns. Many animals live in cold places. The Arctic is very cold."
        },
        {
            "name": "Completely off-topic essay",
            "prompt": "Discuss the impact of climate change on polar bears",
            "essay": "The best pizza toppings are pepperoni and mushroom. I enjoy playing video games in the summer. My favorite color is blue. Basketball is a fun sport to play with friends. Technology advances rapidly each year. Cars have become more efficient."
        },
        {
            "name": "Vaguely related essay",
            "prompt": "Discuss the impact of climate change on polar bears",
            "essay": "Global warming is a serious problem. Scientists study environmental changes. Animals adapt to new conditions. Some species migrate to find better habitats. Human activity affects ecosystems. Weather patterns shift over time."
        }
    ]
    
    print("\n" + "="*80)
    print("SEMANTIC TOPIC RELEVANCE DETECTION TEST")
    print("="*80 + "\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['name']}")
        print(f"Prompt: {test['prompt']}")
        print(f"Essay: {test['essay'][:100]}...")
        
        relevance = service.calculate_semantic_relevance(
            test['essay'],
            test['prompt']
        )
        
        print(f"Relevance Score: {relevance:.1f}/100")
        
        # Determine relevance category
        if relevance >= 80:
            category = "✓ HIGHLY RELEVANT"
        elif relevance >= 60:
            category = "◐ MODERATELY RELEVANT"
        elif relevance >= 40:
            category = "◑ SOMEWHAT RELEVANT"
        else:
            category = "✗ OFF-TOPIC"
        
        print(f"Category: {category}\n")
    
    print("="*80)
    print("Test completed successfully!")
    print("="*80)


if __name__ == "__main__":
    test_topic_relevance()

#!/usr/bin/env python3
"""
Compile (Optimize) the A1 DSPy Agent using the MIPROv2 Optimizer.
"""
import os
import dspy
import litellm

# Import from the local a1_dspy_agent module
from a1_dspy_agent import (
    A1DSPyAgent,
    create_training_examples,
    a1_security_metric,
    configure_dspy_lm
)

def main():
    """
    Main function to run the DSPy optimization process.
    """
    print("🚀 Starting A1 DSPy Agent Compilation with MIPROv2...")
    
    # 1. Configure DSPy to use the Google Gemini model
    try:
        # Explicitly set the model to Gemini for this run
        import os
        os.environ["DSPY_MODEL"] = "gemini"
        configure_dspy_lm()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("   Please ensure the A1_RESEARCH_API_KEY or ANTHROPIC_API_KEY is set.")
        return

    # 2. Load the training data
    training_examples = create_training_examples()
    print(f"✅ Loaded {len(training_examples)} training examples.")

    # Set the global flag for litellm to drop unsupported parameters
    litellm.drop_params = True
    print("✅ Set litellm.drop_params = True to handle unsupported parameters.")

    # 3. Set up the MIPROv2 optimizer
    # MIPRO is a multi-objective optimizer for DSPy programs.
    # It will explore different prompt variations to maximize our metric.
    optimizer = dspy.COPRO(
        prompt_model=dspy.settings.lm,
        task_model=dspy.settings.lm,
        metric=a1_security_metric,
        num_candidates=10,  # Number of prompt candidates to generate
        init_temperature=1.4, # Initial temperature for generation
    )
    print("✅ MIPROv2 optimizer configured.")

    # 4. Instantiate the agent to be optimized
    unoptimized_agent = A1DSPyAgent()

    # 5. Run the optimization (compilation)
    print("\n🔥 Compiling... (This may take 15-20 minutes depending on API latency)")
    optimized_agent = optimizer.compile(
        student=unoptimized_agent,
        trainset=training_examples,
        eval_kwargs={"num_threads": 1}
    )
    print("✅ Compilation complete!")

    # 6. Save the optimized agent's state
    optimized_agent_path = "a1_dspy_compiled_mipro.json"
    optimized_agent.save(optimized_agent_path)
    print(f"\n💾 Optimized agent state saved to: {optimized_agent_path}")

    print("\n🎉 Process finished successfully!")
    print("   You can now load the compiled agent from the saved JSON file for inference.")

if __name__ == "__main__":
    main()

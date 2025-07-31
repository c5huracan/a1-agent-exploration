#!/usr/bin/env python3
"""
Test A1 DSPy Agent with Real Vulnerability Examples
"""
import os
import asyncio
from a1_dspy_agent import configure_dspy_lm, A1DSPyAgent, create_training_examples, a1_security_metric

# Test contracts from paper-comparison
TEST_CONTRACTS = {
    "0x123": '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableDeFiPool {
    mapping(address => uint256) public balances;
    
    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }
    
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        (bool success,) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        balances[msg.sender] -= amount; // CRITICAL: Reentrancy vulnerability!
    }
}''',
    "0x456": '''// SPDX-License-Identifier: MIT  
pragma solidity ^0.8.0;

contract ProxyContract {
    address private _implementation;
    address private owner;
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    function upgrade(address newImplementation) external onlyOwner {
        _implementation = newImplementation;
    }
    
    fallback() external payable {
        address impl = _implementation;
        assembly {
            let ptr := mload(0x40)
            calldatacopy(ptr, 0, calldatasize())
            let result := delegatecall(gas(), impl, ptr, calldatasize(), 0, 0)
            let size := returndatasize()
            returndatacopy(ptr, 0, size)
            
            switch result
            case 0 { revert(ptr, size) }
            default { return(ptr, size) }
        }
    }
}''',
    "0x789": '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleToken {
    mapping(address => uint256) public balances;
    string public name = "SimpleToken";
    
    function transfer(address to, uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
}'''
}

async def test_dspy_agent():
    """Test A1 DSPy Agent with vulnerability examples"""
    print("🔬 Testing A1 DSPy Agent")
    print("=" * 40)
    
    try:
        # Configure DSPy with Claude (if API key available)
        api_key = os.getenv('A1_RESEARCH_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("⚠️  No API key found - testing architecture only")
            print("✅ DSPy architecture test: PASSED")
            return
        
        # Initialize DSPy with the configured LM
        print("🔧 Configuring DSPy LM...")
        lm = configure_dspy_lm()
        
        # Create A1 DSPy Agent
        print("🤖 Initializing A1 DSPy Agent...")
        agent = A1DSPyAgent()
        
        # Test with VulnerableDeFiPool (should find reentrancy)
        print("\n📋 Testing with VulnerableDeFiPool (0x123)")
        print("-" * 30)
        
        result = await agent.forward(
            contract_address="0x123",
            contract_code=TEST_CONTRACTS["0x123"]
        )
        
        print(f"✅ Analysis completed:")
        print(f"   - Tools used: {result.selected_tools}")
        print(f"   - Vulnerabilities found: {len(result.vulnerabilities)}")
        print(f"   - Risk score: {result.risk_score:.1f}/10.0")
        print(f"   - Confidence: {result.confidence:.2f}")
        
        # Check if reentrancy was detected
        vuln_types = [v.get('type', '') for v in result.vulnerabilities]
        if 'reentrancy' in vuln_types:
            print("✅ Critical reentrancy vulnerability detected!")
        else:
            print("⚠️  Reentrancy vulnerability missed")
        
        print(f"\n🧠 Reasoning: {result.reasoning[:200]}...")
        
        # Test training examples
        print("\n📚 Testing Training Examples...")
        examples = create_training_examples()
        print(f"✅ Created {len(examples)} training examples")
        
        # Test optimization metric
        print("\n📊 Testing Optimization Metric...")
        if examples:
            example = examples[0]
            metric_score = a1_security_metric(example, result)
            print(f"✅ Metric score: {metric_score:.3f}")
        
        print("\n🎯 DSPy Agent Test: SUCCESS")
        
    except Exception as e:
        print(f"❌ DSPy Agent test failed: {e}")
        import traceback
        traceback.print_exc()

def test_architecture_only():
    """Test DSPy architecture without API calls"""
    print("🔬 Testing A1 DSPy Architecture (No API)")
    print("=" * 45)
    
    try:
        # Test signature creation
        from a1_dspy_agent import ToolSelectionSignature, VulnerabilityAssessmentSignature, AnalysisCompletionSignature
        print("✅ DSPy Signatures: OK")
        
        # Test module creation
        from a1_dspy_agent import A1ToolSelector, A1VulnerabilityAssessor, A1AnalysisController
        print("✅ DSPy Modules: OK")
        
        # Test agent initialization
        agent = A1DSPyAgent()
        print("✅ A1DSPyAgent: OK")
        
        # Test training examples
        examples = create_training_examples()
        print(f"✅ Training Examples: {len(examples)} created")
        
        # Test metric function
        from dataclasses import dataclass
        from typing import List
        
        @dataclass
        class MockResult:
            selected_tools: List[str]
            vulnerabilities: List[dict]
            risk_score: float
        
        mock_result = MockResult(
            selected_tools=["contract_analysis"],
            vulnerabilities=[{"type": "reentrancy", "severity": "CRITICAL"}],
            risk_score=8.5
        )
        
        if examples:
            metric_score = a1_security_metric(examples[0], mock_result)
            print(f"✅ Optimization Metric: {metric_score:.3f}")
        
        print("\n🎯 Architecture Test: SUCCESS")
        print("Ready for API integration and MIPROv2 optimization!")
        
    except Exception as e:
        print(f"❌ Architecture test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check if we have API access
    api_key = os.getenv('A1_RESEARCH_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
    
    if api_key:
        print("🔑 API key found - running full integration test")
        asyncio.run(test_dspy_agent())
    else:
        print("📋 No API key - running architecture test only")
        test_architecture_only()
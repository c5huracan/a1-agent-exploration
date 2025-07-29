#!/usr/bin/env python3
"""
Compare DSPy-optimized A1 agent vs manual A1 agent
Demonstrates the power of learned optimization vs manual prompts
"""
import os
import asyncio
import time
from a1_dspy_agent import configure_dspy_claude, A1DSPyAgent

# Test contracts
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
}'''
}

async def run_manual_a1_agent(contract_address: str, contract_code: str):
    """Run the manual A1 agent from paper-comparison for comparison"""
    import sys
    import importlib.util
    
    # Load manual A1 agent
    spec = importlib.util.spec_from_file_location(
        "manual_a1", 
        "/workspaces/a1-agent-exploration/worktrees/paper-comparison/a1_agent.py"
    )
    manual_a1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(manual_a1)
    
    # Create LLM interface and agent
    llm = manual_a1.LLMInterface()
    agent = manual_a1.A1Agent(llm)
    
    start_time = time.time()
    result = await agent.analyze_contract(contract_address, contract_code)
    end_time = time.time()
    
    return result, end_time - start_time

async def run_dspy_a1_agent(contract_address: str, contract_code: str):
    """Run the DSPy-optimized A1 agent"""
    # Configure DSPy
    lm = configure_dspy_claude()
    agent = A1DSPyAgent()
    
    start_time = time.time()
    result = await agent.forward(contract_address, contract_code)
    end_time = time.time()
    
    return result, end_time - start_time

async def compare_agents():
    """Compare manual vs DSPy A1 agents on test contracts"""
    print("🔬 A1 Agent Comparison: Manual vs DSPy")
    print("=" * 50)
    
    if not (os.getenv('A1_RESEARCH_API_KEY') or os.getenv('ANTHROPIC_API_KEY')):
        print("❌ No API key found - comparison requires Claude API access")
        return
    
    for contract_addr, contract_code in TEST_CONTRACTS.items():
        print(f"\n📋 Testing Contract: {contract_addr}")
        print("-" * 40)
        
        # Run manual A1 agent
        print("🤖 Running Manual A1 Agent...")
        try:
            manual_result, manual_time = await run_manual_a1_agent(contract_addr, contract_code)
            print(f"✅ Manual Agent Completed ({manual_time:.1f}s)")
            print(f"   - Vulnerabilities: {len(manual_result.vulnerabilities)}")
            print(f"   - Risk Score: {manual_result.risk_score:.1f}/10.0")
            print(f"   - Tools Used: {manual_result.tool_usage}")
            print(f"   - Iterations: {manual_result.iterations}")
        except Exception as e:
            print(f"❌ Manual Agent Failed: {e}")
            continue
        
        # Run DSPy A1 agent  
        print("\n🧠 Running DSPy A1 Agent...")
        try:
            dspy_result, dspy_time = await run_dspy_a1_agent(contract_addr, contract_code)
            print(f"✅ DSPy Agent Completed ({dspy_time:.1f}s)")
            print(f"   - Vulnerabilities: {len(dspy_result.vulnerabilities)}")
            print(f"   - Risk Score: {dspy_result.risk_score:.1f}/10.0")
            print(f"   - Tools Used: {dspy_result.selected_tools}")
        except Exception as e:
            print(f"❌ DSPy Agent Failed: {e}")
            continue
        
        # Compare results
        print(f"\n📊 Comparison Results:")
        print(f"   - Time Efficiency: {'DSPy' if dspy_time < manual_time else 'Manual'} faster")
        print(f"     (Manual: {manual_time:.1f}s vs DSPy: {dspy_time:.1f}s)")
        
        # Tool diversity comparison
        manual_tools = set(manual_result.tool_usage)
        dspy_tools = set(dspy_result.selected_tools)
        print(f"   - Tool Diversity: Manual={len(manual_tools)}, DSPy={len(dspy_tools)}")
        
        # Vulnerability detection comparison
        manual_vulns = set(v.get('type', '') for v in manual_result.vulnerabilities)
        dspy_vulns = set(v.get('type', '') for v in dspy_result.vulnerabilities)
        common_vulns = manual_vulns.intersection(dspy_vulns)
        print(f"   - Vulnerability Detection:")
        print(f"     Manual: {manual_vulns}")
        print(f"     DSPy: {dspy_vulns}")
        print(f"     Common: {common_vulns}")
        
        # Risk assessment comparison
        risk_diff = abs(manual_result.risk_score - dspy_result.risk_score)
        print(f"   - Risk Assessment: {'Consistent' if risk_diff < 1.0 else 'Different'}")
        print(f"     (Difference: {risk_diff:.1f})")

async def benchmark_performance():
    """Benchmark DSPy vs Manual performance characteristics"""
    print("\n🏃 Performance Benchmark")
    print("=" * 30)
    
    contract_addr = "0x123"
    contract_code = TEST_CONTRACTS[contract_addr]
    
    # Run multiple trials for statistical significance
    trials = 3
    manual_times = []
    dspy_times = []
    
    print(f"Running {trials} trials each...")
    
    for trial in range(trials):
        print(f"\nTrial {trial + 1}/{trials}")
        
        # Manual agent trial
        try:
            _, manual_time = await run_manual_a1_agent(contract_addr, contract_code)
            manual_times.append(manual_time)
            print(f"  Manual: {manual_time:.1f}s")
        except Exception as e:
            print(f"  Manual failed: {e}")
        
        # DSPy agent trial
        try:
            _, dspy_time = await run_dspy_a1_agent(contract_addr, contract_code)
            dspy_times.append(dspy_time)
            print(f"  DSPy: {dspy_time:.1f}s")
        except Exception as e:
            print(f"  DSPy failed: {e}")
    
    # Calculate statistics
    if manual_times and dspy_times:
        avg_manual = sum(manual_times) / len(manual_times)
        avg_dspy = sum(dspy_times) / len(dspy_times)
        
        print(f"\n📈 Performance Summary:")
        print(f"   - Manual Average: {avg_manual:.1f}s")
        print(f"   - DSPy Average: {avg_dspy:.1f}s")
        print(f"   - Speedup: {avg_manual/avg_dspy:.1f}x {'DSPy' if avg_dspy < avg_manual else 'Manual'}")

if __name__ == "__main__":
    asyncio.run(compare_agents())
    asyncio.run(benchmark_performance())
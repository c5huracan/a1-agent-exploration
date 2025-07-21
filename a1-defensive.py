class A1DefensiveAgent:
    """Main agent that coordinates defensive security analysis using multiple tools"""
    def __init__(self, llm_model):
        self.llm = llm_model  # LLM for reasoning and code generation
        self.tools = {}       # Registry of available tools

    def register_tool(self, name, tool_instance):
        """Register a tool for use by the agent"""
        self.tools[name] = tool_instance
    '''
    # Execute v0.1
    def execute(self, blockchain, contract_address, block_number, **kwargs):
        """Main exploit generation method - coordinates tools to find vulnerabilities"""
        # Step 1: Fetch source code
        source_result = self.tools['fetcher'].execute(blockchain, contract_address, block_number)
        
        # Step 2: Get constructor parameters
        param_result = self.tools['params'].execute(blockchain, contract_address, block_number)
        
        # Step 3: Generate exploit (mock for now)
        return {"status": "success", "exploit_found": True, "source": source_result, "params": param_result}
    '''
    '''
    # Execute v0.2
    def execute(self, blockchain, contract_address, block_number, **kwargs):
        """Main exploit generation method - coordinates tools to find vulnerabilities"""
        # Step 1: Fetch and clean source code
        source_result = self.tools['fetcher'].execute(blockchain, contract_address, block_number)
        clean_result = self.tools['sanitizer'].execute(source_result['source_code'])
        
        # Step 2: Get parameters and state
        param_result = self.tools['params'].execute(blockchain, contract_address, block_number)
        state_result = self.tools['state'].execute(blockchain, contract_address, block_number)
        
        # Step 3: Test exploit and calculate revenue
        execution_result = self.tools['execution'].execute("mock_exploit", blockchain, block_number)
        revenue_result = self.tools['revenue'].execute(["token1", "token2"])
        
        return {"status": "success", "exploit_found": True, "revenue": revenue_result}
        '''

    # Execute v0.4 - Defensive Analysis
    def execute(self, blockchain, contract_address, block_number, **kwargs):
        """Main defensive analysis method - coordinates tools to assess security posture"""
        max_iterations = 5
        iteration_history = []
        
        for iteration in range(max_iterations):
            tools_list = ", ".join(self.tools.keys())
            prompt = f"Available tools: {tools_list}. Perform security assessment of contract at {contract_address} on {blockchain}. Which tool should I use first?"
            if iteration_history:
                prompt += f" Also, analyze the iteration history: {iteration_history}."
            response = self.llm.generate(prompt)
            tool_name = parse_tool_decision(response)
            if tool_name in self.tools:
                result = self.tools[tool_name].execute(blockchain, contract_address, block_number)
                iteration_history.append({"tool": tool_name, "result": result})
                if result.get("status") == "success" and result.get("profitable"):
                    return result

            else:
                return {"status": "error", "message": "Tool not found"}
        
        return {"status": "max_iterations_reached", "message": "No successful exploit found"}

class BaseTool:
    """Base class for all A1 tools - defines common interface"""
    def __init__(self, name):
        self.name = name  # Human-readable tool name

    def execute(self, **params):
        """Execute the tool with given parameters - must be implemented by subclasses"""
        raise NotImplementedError

    @property
    def description(self):
        """Return description of tool's purpose and capabilities"""
        raise NotImplementedError

class DummyTool(BaseTool):
    """Simple test tool for validating the A1 system architecture"""
    @property
    def description(self):
        """Returns basic description for testing purposes"""
        return "A test tool"

    def execute(self, **params):
        """Returns success message to verify tool execution works"""
        return {"status": "success", "message": "dummy tool executed"}

class MockLLM:
    def generate(self, prompt):
        return "I should use the fetcher tool to get the source code first."

def parse_tool_decision(response):
    for tool_name in ["fetcher", "params", "state", "sanitizer", "execution", "revenue"]:
        if tool_name in response.lower():
            return tool_name
    return None

# A1 Tools
class SourceCodeFetcher(BaseTool):
    """Fetches smart contract source code and handles proxy contract resolution"""
    
    def __init__(self, name):
        super().__init__(name)
        # Mock contract database - realistic examples based on common DeFi patterns
        self.contract_database = {
            "0x123": self._get_vulnerable_defi_contract(),
            "0x456": self._get_proxy_contract(),
            "0x789": self._get_token_contract(),
        }
    
    @property
    def description(self):
        return "Fetches smart contract source code and handles proxy resolution"

    def execute(self, blockchain, contract_address, block_number, **kwargs):
        """Fetch source code for contract at specific block"""
        
        # Simulate realistic response times
        import time
        time.sleep(0.1)  # Simulate network delay
        
        # Get mock contract or return error
        if contract_address in self.contract_database:
            source_code = self.contract_database[contract_address]
            return {
                "status": "success", 
                "source_code": source_code,
                "compiler_version": "0.8.19",
                "optimization": True,
                "is_proxy": "Proxy" in source_code,
                "implementation_address": "0xabc123" if "Proxy" in source_code else None
            }
        else:
            return {
                "status": "error",
                "error": "Contract not verified or not found",
                "source_code": None
            }
    
    def _get_vulnerable_defi_contract(self):
        """Returns a realistic DeFi contract with potential vulnerabilities for analysis"""
        return '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableDeFiPool {
    mapping(address => uint256) public balances;
    mapping(address => mapping(address => uint256)) public allowances;
    
    uint256 public totalSupply;
    uint256 public constant INITIAL_PRICE = 1e18;
    
    event Deposit(address indexed user, uint256 amount);
    event Withdraw(address indexed user, uint256 amount);
    
    constructor() {
        totalSupply = 1000000 * 1e18;
        balances[msg.sender] = totalSupply;
    }
    
    function deposit(uint256 amount) external {
        require(amount > 0, "Amount must be positive");
        // Potential reentrancy vulnerability - state change after external call
        balances[msg.sender] += amount;
        emit Deposit(msg.sender, amount);
    }
    
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        // Potential reentrancy - external call before state change
        (bool success,) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        balances[msg.sender] -= amount; // State change after external call
        emit Withdraw(msg.sender, amount);
    }
    
    function getPrice() external pure returns (uint256) {
        return INITIAL_PRICE; // Simplified pricing - could be manipulated
    }
    
    // Potential overflow in older Solidity versions
    function unsafeAdd(uint256 a, uint256 b) external pure returns (uint256) {
        return a + b; // No overflow check in pre-0.8.0
    }
}'''

    def _get_proxy_contract(self):
        """Returns a realistic proxy contract pattern"""
        return '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TransparentUpgradeableProxy {
    bytes32 private constant _IMPLEMENTATION_SLOT = 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc;
    bytes32 private constant _ADMIN_SLOT = 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103;
    
    constructor(address implementation, bytes memory data) {
        _setImplementation(implementation);
        _setAdmin(msg.sender);
        
        if (data.length > 0) {
            (bool success,) = implementation.delegatecall(data);
            require(success, "Initialization failed");
        }
    }
    
    fallback() external payable {
        _delegate(_implementation());
    }
    
    receive() external payable {
        _delegate(_implementation());
    }
    
    function _implementation() internal view returns (address impl) {
        bytes32 slot = _IMPLEMENTATION_SLOT;
        assembly {
            impl := sload(slot)
        }
    }
    
    function _setImplementation(address newImplementation) private {
        bytes32 slot = _IMPLEMENTATION_SLOT;
        assembly {
            sstore(slot, newImplementation)
        }
    }
    
    function _admin() internal view returns (address adm) {
        bytes32 slot = _ADMIN_SLOT;
        assembly {
            adm := sload(slot)
        }
    }
    
    function _setAdmin(address newAdmin) private {
        bytes32 slot = _ADMIN_SLOT;
        assembly {
            sstore(slot, newAdmin)
        }
    }
    
    function _delegate(address implementation) internal {
        assembly {
            calldatacopy(0, 0, calldatasize())
            let result := delegatecall(gas(), implementation, 0, calldatasize(), 0, 0)
            returndatacopy(0, 0, returndatasize())
            switch result
            case 0 { revert(0, returndatasize()) }
            default { return(0, returndatasize()) }
        }
    }
}'''

    def _get_token_contract(self):
        """Returns a realistic ERC20 token contract"""
        return '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract RealisticToken {
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;
    
    uint256 private _totalSupply;
    string private _name;
    string private _symbol;
    uint8 private _decimals;
    address private _owner;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    
    constructor(string memory name_, string memory symbol_) {
        _name = name_;
        _symbol = symbol_;
        _decimals = 18;
        _totalSupply = 1000000 * 10**_decimals;
        _owner = msg.sender;
        _balances[msg.sender] = _totalSupply;
        emit Transfer(address(0), msg.sender, _totalSupply);
    }
    
    function name() external view returns (string memory) { return _name; }
    function symbol() external view returns (string memory) { return _symbol; }
    function decimals() external view returns (uint8) { return _decimals; }
    function totalSupply() external view returns (uint256) { return _totalSupply; }
    function balanceOf(address account) external view returns (uint256) { return _balances[account]; }
    
    function transfer(address to, uint256 amount) external returns (bool) {
        _transfer(msg.sender, to, amount);
        return true;
    }
    
    function allowance(address owner, address spender) external view returns (uint256) {
        return _allowances[owner][spender];
    }
    
    function approve(address spender, uint256 amount) external returns (bool) {
        _approve(msg.sender, spender, amount);
        return true;
    }
    
    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        uint256 currentAllowance = _allowances[from][msg.sender];
        require(currentAllowance >= amount, "ERC20: transfer amount exceeds allowance");
        
        _transfer(from, to, amount);
        _approve(from, msg.sender, currentAllowance - amount);
        
        return true;
    }
    
    function _transfer(address from, address to, uint256 amount) internal {
        require(from != address(0), "ERC20: transfer from the zero address");
        require(to != address(0), "ERC20: transfer to the zero address");
        
        uint256 fromBalance = _balances[from];
        require(fromBalance >= amount, "ERC20: transfer amount exceeds balance");
        
        _balances[from] = fromBalance - amount;
        _balances[to] += amount;
        
        emit Transfer(from, to, amount);
    }
    
    function _approve(address owner, address spender, uint256 amount) internal {
        require(owner != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");
        
        _allowances[owner][spender] = amount;
        emit Approval(owner, spender, amount);
    }
}'''

class ConstructorParameterTool(BaseTool):
    """Extracts constructor parameters from smart contract initialization"""
    
    def __init__(self, name):
        super().__init__(name)
        # Mock deployment database with realistic constructor parameters
        self.deployment_database = {
            "0x123": {  # VulnerableDeFiPool
                "deployment_tx": "0xabc123def456789",
                "deployer": "0x742d35Cc6634C0532925a3b8D69d26E1D999D52f",
                "block_number": 17892345,
                "constructor_params": {},  # No constructor parameters
                "creation_code": "0x608060405234801561001057600080fd5b50...",
                "gas_used": 1234567,
                "gas_price": 20000000000
            },
            "0x456": {  # TransparentUpgradeableProxy  
                "deployment_tx": "0xdef456abc789012",
                "deployer": "0x8ba1f109551bD432803012645Hac136c22AfD80A",
                "block_number": 17892346,
                "constructor_params": {
                    "implementation": "0x1234567890abcdef1234567890abcdef12345678",
                    "admin": "0x742d35Cc6634C0532925a3b8D69d26E1D999D52f",
                    "data": "0xc4d66de8000000000000000000000000742d35cc6634c0532925a3b8d69d26e1d999d52f"
                },
                "creation_code": "0x608060405234801561001057600080fd5b50604051...",
                "gas_used": 2456789,
                "gas_price": 25000000000
            },
            "0x789": {  # RealisticToken
                "deployment_tx": "0x789abc012def345",
                "deployer": "0x742d35Cc6634C0532925a3b8D69d26E1D999D52f",
                "block_number": 17892347,
                "constructor_params": {
                    "name": "Vulnerable Token",
                    "symbol": "VULN",
                    "initialSupply": "1000000000000000000000000"
                },
                "creation_code": "0x60806040523480156100105760008...",
                "gas_used": 1876543,
                "gas_price": 22000000000
            }
        }
    
    @property
    def description(self):
        return "Extracts constructor parameters from smart contract initialization"

    def execute(self, blockchain, contract_address, block_number, **kwargs):
        """Extract constructor parameters from deployment transaction"""
        
        import time
        time.sleep(0.05)  # Simulate blockchain query delay
        
        if contract_address in self.deployment_database:
            deployment_data = self.deployment_database[contract_address]
            
            # Simulate historical block analysis
            if block_number < deployment_data["block_number"]:
                return {
                    "status": "error",
                    "error": f"Contract was deployed at block {deployment_data['block_number']}, cannot analyze at earlier block {block_number}",
                    "parameters": None
                }
            
            return {
                "status": "success",
                "parameters": deployment_data["constructor_params"],
                "deployment_transaction": deployment_data["deployment_tx"],
                "deployer_address": deployment_data["deployer"],
                "deployment_block": deployment_data["block_number"],
                "gas_used": deployment_data["gas_used"],
                "gas_price": deployment_data["gas_price"],
                "creation_code_hash": self._get_creation_code_hash(deployment_data["creation_code"]),
                "analysis": self._analyze_constructor_security(deployment_data["constructor_params"])
            }
        else:
            return {
                "status": "error", 
                "error": "Deployment transaction not found or contract address invalid",
                "parameters": None
            }
    
    def _get_creation_code_hash(self, creation_code):
        """Simulate creation code hash calculation"""
        import hashlib
        return hashlib.sha256(creation_code.encode()).hexdigest()[:16]
    
    def _analyze_constructor_security(self, params):
        """Analyze constructor parameters for potential security issues"""
        analysis = {
            "risk_level": "low",
            "findings": [],
            "recommendations": []
        }
        
        if not params:
            analysis["findings"].append("No constructor parameters - state initialized to default values")
            return analysis
        
        # Check for admin/owner parameters
        admin_keys = ["admin", "owner", "deployer", "governance"]
        for key in params:
            if any(admin_key in key.lower() for admin_key in admin_keys):
                if params[key] == "0x0000000000000000000000000000000000000000":
                    analysis["risk_level"] = "high"
                    analysis["findings"].append(f"Zero address set for {key} - potential access control issue")
                else:
                    analysis["findings"].append(f"Privileged address {key}: {params[key]}")
        
        # Check for implementation addresses (proxy patterns)
        if "implementation" in params:
            analysis["findings"].append("Proxy pattern detected - implementation can be upgraded")
            if params["implementation"] == "0x0000000000000000000000000000000000000000":
                analysis["risk_level"] = "high"
                analysis["findings"].append("Zero implementation address - proxy is broken")
        
        # Check for large initial values
        for key, value in params.items():
            if isinstance(value, str) and value.isdigit():
                if len(value) > 15:  # Very large numbers
                    analysis["findings"].append(f"Large initial value for {key}: {value}")
        
        # Add recommendations based on findings
        if analysis["risk_level"] == "high":
            analysis["recommendations"].append("Review access control mechanisms")
            analysis["recommendations"].append("Verify all privileged addresses are correct")
        
        return analysis

class StateReaderTool(BaseTool):
    """Queries contract functions to understand current state"""
    
    def __init__(self, name):
        super().__init__(name)
        # Mock state database with realistic contract states at different blocks
        self.state_database = {
            "0x123": {  # VulnerableDeFiPool
                "functions": ["balances", "totalSupply", "getPrice", "allowances"],
                "state_history": {
                    17892345: {  # Deployment block
                        "totalSupply": "1000000000000000000000000",  # 1M tokens
                        "balances": {
                            "0x742d35Cc6634C0532925a3b8D69d26E1D999D52f": "1000000000000000000000000"
                        },
                        "contract_balance": "0",  # ETH balance
                        "price": "1000000000000000000"  # 1 ETH
                    },
                    17900000: {  # Later block with activity
                        "totalSupply": "1000000000000000000000000", 
                        "balances": {
                            "0x742d35Cc6634C0532925a3b8D69d26E1D999D52f": "800000000000000000000000",
                            "0x1234567890abcdef1234567890abcdef12345678": "150000000000000000000000",
                            "0xabc123def456789abc123def456789abc123def": "50000000000000000000000"
                        },
                        "contract_balance": "500000000000000000000",  # 500 ETH deposited
                        "price": "1200000000000000000"  # Price increased
                    }
                }
            },
            "0x456": {  # TransparentUpgradeableProxy
                "functions": ["implementation", "admin", "upgradeTo", "changeAdmin"],
                "state_history": {
                    17892346: {
                        "implementation": "0x1234567890abcdef1234567890abcdef12345678",
                        "admin": "0x742d35Cc6634C0532925a3b8D69d26E1D999D52f",
                        "contract_balance": "0"
                    },
                    17950000: {  # After upgrade
                        "implementation": "0x9876543210fedcba9876543210fedcba98765432",  # New implementation
                        "admin": "0x742d35Cc6634C0532925a3b8D69d26E1D999D52f",
                        "contract_balance": "1000000000000000000000"  # 1000 ETH
                    }
                }
            },
            "0x789": {  # RealisticToken  
                "functions": ["name", "symbol", "totalSupply", "balanceOf", "allowance"],
                "state_history": {
                    17892347: {  # Deployment
                        "name": "Vulnerable Token",
                        "symbol": "VULN", 
                        "decimals": 18,
                        "totalSupply": "1000000000000000000000000",
                        "balances": {
                            "0x742d35Cc6634C0532925a3b8D69d26E1D999D52f": "1000000000000000000000000"
                        },
                        "allowances": {}
                    },
                    18000000: {  # After trading activity
                        "name": "Vulnerable Token",
                        "symbol": "VULN",
                        "decimals": 18, 
                        "totalSupply": "1000000000000000000000000",
                        "balances": {
                            "0x742d35Cc6634C0532925a3b8D69d26E1D999D52f": "600000000000000000000000",
                            "0x1111111111111111111111111111111111111111": "200000000000000000000000", 
                            "0x2222222222222222222222222222222222222222": "150000000000000000000000",
                            "0x3333333333333333333333333333333333333333": "50000000000000000000000"
                        },
                        "allowances": {
                            "0x742d35Cc6634C0532925a3b8D69d26E1D999D52f": {
                                "0x1111111111111111111111111111111111111111": "100000000000000000000000"
                            }
                        }
                    }
                }
            }
        }
    
    @property
    def description(self):
        return "Reads contract state via function calls at specific block heights"
    
    def execute(self, blockchain, contract_address, block_number, **kwargs):
        """Query contract state at specific block"""
        
        import time
        time.sleep(0.08)  # Simulate RPC query delay
        
        if contract_address not in self.state_database:
            return {
                "status": "error",
                "error": "Contract address not found or not supported for state queries",
                "state": None
            }
        
        contract_data = self.state_database[contract_address]
        
        # Find the appropriate historical state
        available_blocks = sorted(contract_data["state_history"].keys())
        target_block = None
        
        for block in available_blocks:
            if block <= block_number:
                target_block = block
            else:
                break
        
        if target_block is None:
            return {
                "status": "error", 
                "error": f"No state data available for block {block_number}. Contract may not have been deployed yet.",
                "state": None
            }
        
        state = contract_data["state_history"][target_block].copy()
        
        return {
            "status": "success",
            "state": state,
            "available_functions": contract_data["functions"],
            "queried_block": target_block,
            "latest_available_block": max(available_blocks),
            "state_analysis": self._analyze_state_security(state, contract_address),
            "balance_distribution": self._analyze_balance_distribution(state),
            "risk_indicators": self._identify_risk_indicators(state, contract_address)
        }
    
    def _analyze_state_security(self, state, contract_address):
        """Analyze state for potential security issues"""
        analysis = {
            "concentration_risk": "low",
            "findings": [],
            "admin_control": []
        }
        
        # Check for admin/owner concentration
        if "admin" in state or "owner" in state:
            admin_addr = state.get("admin") or state.get("owner")
            if admin_addr and admin_addr != "0x0000000000000000000000000000000000000000":
                analysis["admin_control"].append(f"Admin/Owner: {admin_addr}")
        
        # Check balance distribution for concentration risk
        if "balances" in state:
            balances = state["balances"]
            if balances:
                total_supply = sum(int(balance) for balance in balances.values())
                max_balance = max(int(balance) for balance in balances.values()) 
                
                if total_supply > 0:
                    concentration = (max_balance / total_supply) * 100
                    if concentration > 50:
                        analysis["concentration_risk"] = "high"
                        analysis["findings"].append(f"High concentration: {concentration:.1f}% held by single address")
                    elif concentration > 20:
                        analysis["concentration_risk"] = "medium"
                        analysis["findings"].append(f"Medium concentration: {concentration:.1f}% held by single address")
        
        # Check contract ETH balance for flash loan risks
        if "contract_balance" in state:
            eth_balance = int(state["contract_balance"])
            if eth_balance > 100 * 10**18:  # > 100 ETH
                analysis["findings"].append(f"Large ETH balance: {eth_balance / 10**18:.2f} ETH - potential flash loan target")
        
        return analysis
    
    def _analyze_balance_distribution(self, state):
        """Analyze token/balance distribution patterns"""
        if "balances" not in state:
            return {"distribution": "no_balance_data"}
        
        balances = state["balances"]
        if not balances:
            return {"distribution": "no_balances"}
        
        balance_values = [int(balance) for balance in balances.values()]
        total = sum(balance_values)
        
        if total == 0:
            return {"distribution": "zero_supply"}
        
        # Calculate distribution metrics
        sorted_balances = sorted(balance_values, reverse=True)
        
        return {
            "distribution": "analyzed",
            "total_holders": len(balances),
            "top_holder_percentage": (sorted_balances[0] / total * 100) if sorted_balances else 0,
            "top_3_percentage": (sum(sorted_balances[:3]) / total * 100) if len(sorted_balances) >= 3 else 100,
            "gini_coefficient": self._calculate_gini(sorted_balances) if len(sorted_balances) > 1 else 0
        }
    
    def _identify_risk_indicators(self, state, contract_address):
        """Identify specific risk indicators based on state"""
        risks = []
        
        # Check for zero balances (potential draining)
        if "contract_balance" in state and int(state["contract_balance"]) == 0:
            if contract_address == "0x123":  # DeFi pool should have balance
                risks.append("DeFi pool has zero ETH balance - potential liquidity issue")
        
        # Check for implementation changes (proxy contracts)
        if "implementation" in state:
            risks.append("Upgradeable proxy - implementation can be changed by admin")
        
        # Check for large allowances
        if "allowances" in state and state["allowances"]:
            for owner, spenders in state["allowances"].items():
                for spender, allowance in spenders.items():
                    if int(allowance) > 10**24:  # Very large allowance
                        risks.append(f"Large token allowance detected: {int(allowance) / 10**18:.0f} tokens")
        
        return risks
    
    def _calculate_gini(self, balances):
        """Calculate Gini coefficient for balance distribution"""
        if len(balances) < 2:
            return 0
        
        balances = sorted(balances)
        n = len(balances)
        cumsum = sum(balances)
        
        if cumsum == 0:
            return 0
        
        # Calculate Gini coefficient
        gini = 0
        for i in range(n):
            gini += (2 * (i + 1) - n - 1) * balances[i]
        
        return gini / (n * cumsum)

class CodeSanitizerTool(BaseTool):
    """Removes extraneous elements from contract code"""
    @property
    def description(self):
        return "Cleans and sanitizes contract code for analysis"
    
    def execute(self, source_code, **kwargs):
        return {"status": "success", "cleaned_code": "// Sanitized contract code"}

class ConcreteExecutionTool(BaseTool):
    """Validates exploit strategies against blockchain states"""
    @property
    def description(self):
        return "Tests exploits on forked blockchain states"
    
    def execute(self, exploit_code, blockchain, block_number, **kwargs):
        return {"status": "success", "profitable": True, "revenue": 1000}

class RevenueNormalizerTool(BaseTool):
    """Converts extracted tokens to native currency"""
    @property
    def description(self):
        return "Normalizes token values to native currency"
    
    def execute(self, tokens, **kwargs):
        return {"status": "success", "usd_value": 5000}

class DefensiveAnalysisTool(BaseTool):
    """Generates comprehensive security assessment reports"""
    @property
    def description(self):
        return "Performs defensive security analysis and generates vulnerability reports"
    
    def __init__(self, name):
        super().__init__(name)
        self.vulnerability_patterns = {
            'reentrancy': ['call{value:', 'external call', 'state change after', 'balances[', 'msg.sender.call'],
            'access_control': ['onlyOwner', 'require(msg.sender', 'modifier', '_ADMIN_SLOT'],
            'integer_overflow': ['SafeMath', 'unchecked', 'overflow', 'unsafeAdd'],
            'proxy_risks': ['delegatecall', '_IMPLEMENTATION_SLOT', 'TransparentUpgradeableProxy', '_setImplementation'],
            'flash_loan_attacks': ['flashloan', 'borrow', 'temporary balance', 'getPrice']
        }
    
    def execute(self, source_code=None, state_data=None, deployment_data=None, **kwargs):
        """Generate comprehensive security assessment report"""
        
        # Analyze source code for vulnerability patterns
        vulnerabilities_found = []
        if source_code:
            for vuln_type, patterns in self.vulnerability_patterns.items():
                for pattern in patterns:
                    if pattern.lower() in source_code.lower():
                        vulnerabilities_found.append({
                            'type': vuln_type,
                            'severity': self._assess_severity(vuln_type, source_code),
                            'pattern': pattern,
                            'description': self._get_vulnerability_description(vuln_type)
                        })
        
        # Analyze state data for concentration risks
        concentration_risks = []
        if state_data and 'balance_distribution' in state_data:
            gini = state_data.get('gini_coefficient', 0)
            if gini > 0.8:
                concentration_risks.append({
                    'type': 'high_concentration',
                    'severity': 'HIGH',
                    'value': gini,
                    'description': 'Wealth highly concentrated - governance/manipulation risk'
                })
        
        # Analyze deployment risks
        deployment_risks = []
        if deployment_data:
            if deployment_data.get('risk_level') == 'HIGH':
                deployment_risks.append({
                    'type': 'deployment_anomaly',
                    'severity': 'HIGH',
                    'description': deployment_data.get('risk_factors', [])
                })
        
        # Generate defensive recommendations
        recommendations = self._generate_recommendations(
            vulnerabilities_found, concentration_risks, deployment_risks
        )
        
        return {
            'status': 'success',
            'vulnerabilities': vulnerabilities_found,
            'concentration_risks': concentration_risks,
            'deployment_risks': deployment_risks,
            'recommendations': recommendations,
            'overall_risk': self._calculate_overall_risk(
                vulnerabilities_found, concentration_risks, deployment_risks
            ),
            'timestamp': kwargs.get('block_number', 'unknown')
        }
    
    def _assess_severity(self, vuln_type, source_code):
        """Assess vulnerability severity based on type and context"""
        high_risk = ['reentrancy', 'access_control', 'proxy_risks']
        if vuln_type in high_risk:
            return 'HIGH'
        elif 'critical' in source_code.lower() or 'emergency' in source_code.lower():
            return 'CRITICAL'
        else:
            return 'MEDIUM'
    
    def _get_vulnerability_description(self, vuln_type):
        """Get detailed description for vulnerability type"""
        descriptions = {
            'reentrancy': 'Contract may be vulnerable to reentrancy attacks during external calls',
            'access_control': 'Access control mechanisms detected - verify proper implementation',
            'integer_overflow': 'Potential integer overflow/underflow vulnerabilities',
            'proxy_risks': 'Proxy pattern detected - upgrade mechanisms require careful review',
            'flash_loan_attacks': 'Contract may be vulnerable to flash loan manipulation attacks'
        }
        return descriptions.get(vuln_type, 'Unknown vulnerability pattern detected')
    
    def _generate_recommendations(self, vulns, concentration, deployment):
        """Generate defensive recommendations based on findings"""
        recommendations = []
        
        # Vulnerability-based recommendations
        for vuln in vulns:
            if vuln['type'] == 'reentrancy':
                recommendations.append('Implement checks-effects-interactions pattern')
                recommendations.append('Consider using ReentrancyGuard modifier')
            elif vuln['type'] == 'access_control':
                recommendations.append('Audit all access control mechanisms')
                recommendations.append('Consider multi-signature requirements for critical functions')
            elif vuln['type'] == 'proxy_risks':
                recommendations.append('Implement upgrade timelock mechanisms')
                recommendations.append('Use transparent proxy patterns with proper governance')
        
        # Concentration-based recommendations
        if concentration:
            recommendations.append('Monitor token distribution for manipulation risks')
            recommendations.append('Implement governance safeguards against whale attacks')
            recommendations.append('Consider voting power caps or delegation mechanisms')
        
        # Deployment-based recommendations
        if deployment:
            recommendations.append('Verify deployment parameters and initial state')
            recommendations.append('Monitor for unusual post-deployment activity')
        
        # General recommendations
        recommendations.extend([
            'Conduct regular security audits',
            'Implement comprehensive testing including edge cases',
            'Monitor contract interactions for suspicious patterns',
            'Maintain emergency pause mechanisms where appropriate'
        ])
        
        return list(set(recommendations))  # Remove duplicates
    
    def _calculate_overall_risk(self, vulns, concentration, deployment):
        """Calculate overall risk assessment"""
        risk_score = 0
        
        # Vulnerability scoring
        for vuln in vulns:
            if vuln['severity'] == 'CRITICAL':
                risk_score += 10
            elif vuln['severity'] == 'HIGH':
                risk_score += 5
            elif vuln['severity'] == 'MEDIUM':
                risk_score += 2
        
        # Concentration risk scoring
        risk_score += len(concentration) * 3
        
        # Deployment risk scoring
        risk_score += len(deployment) * 4
        
        # Overall assessment
        if risk_score >= 15:
            return 'CRITICAL'
        elif risk_score >= 8:
            return 'HIGH'
        elif risk_score >= 3:
            return 'MEDIUM'
        else:
            return 'LOW'

def run_defensive_analysis_tests():
    """Test the defensive security analysis system"""
    print("=== Defensive Security Analysis Tests ===\n")
    
    # Initialize defensive agent
    agent = A1DefensiveAgent(MockLLM())
    
    # Register all tools including the new defensive analysis tool
    agent.register_tool("fetcher", SourceCodeFetcher("SourceCodeFetcher"))
    agent.register_tool("params", ConstructorParameterTool("ConstructorParameterTool"))
    agent.register_tool("state", StateReaderTool("StateReaderTool"))
    agent.register_tool("sanitizer", CodeSanitizerTool("CodeSanitizerTool"))
    agent.register_tool("execution", ConcreteExecutionTool("ConcreteExecutionTool"))
    agent.register_tool("revenue", RevenueNormalizerTool("RevenueNormalizerTool"))
    agent.register_tool("defense", DefensiveAnalysisTool("DefensiveAnalysisTool"))
    
    # Test contracts for defensive analysis (using addresses from contract database)
    test_contracts = [
        ("ethereum", "0x123", 17900000, "VulnerableDeFiPool - High Risk"),
        ("ethereum", "0x789", 18000000, "RealisticToken - Medium Risk"),
        ("ethereum", "0x456", 17950000, "Proxy Contract - Upgrade Risk")
    ]
    
    for blockchain, address, block, description in test_contracts:
        print(f"🛡️  Defensive Analysis: {description}")
        print(f"   Contract: {address} on {blockchain} at block {block}")
        
        # Get contract data
        fetcher = SourceCodeFetcher("SourceCodeFetcher")
        params_tool = ConstructorParameterTool("ConstructorParameterTool")
        state_tool = StateReaderTool("StateReaderTool")
        defense_tool = DefensiveAnalysisTool("DefensiveAnalysisTool")
        
        # Fetch contract information
        source_data = fetcher.execute(blockchain, address, block)
        deployment_data = params_tool.execute(blockchain, address, block)
        state_data = state_tool.execute(blockchain, address, block)
        
        # Check if we have concentration risks from state data
        concentration_risks = []
        if state_data and state_data.get('status') == 'success':
            gini = state_data.get('gini_coefficient', 0)
            if gini > 0.8:
                concentration_risks.append({
                    'type': 'high_concentration',
                    'severity': 'HIGH', 
                    'value': gini,
                    'description': f'High wealth concentration (Gini: {gini:.2f}) - governance manipulation risk'
                })
        
        # Check deployment risks  
        deployment_risks = []
        if deployment_data and deployment_data.get('risk_level') == 'HIGH':
            deployment_risks.append({
                'type': 'deployment_anomaly',
                'severity': 'HIGH',
                'description': deployment_data.get('risk_factors', [])
            })
        
        # Perform defensive analysis 
        analysis_result = defense_tool.execute(
            source_code=source_data.get('source_code'),
            state_data=state_data,
            deployment_data=deployment_data,
            block_number=block
        )
        
        # Add our manually detected risks to the analysis
        analysis_result['concentration_risks'].extend(concentration_risks)
        analysis_result['deployment_risks'].extend(deployment_risks)
        
        # Recalculate overall risk with new information
        total_vulns = len(analysis_result['vulnerabilities'])
        total_concentration = len(analysis_result['concentration_risks']) 
        total_deployment = len(analysis_result['deployment_risks'])
        
        risk_score = (total_vulns * 2) + (total_concentration * 3) + (total_deployment * 4)
        if risk_score >= 15:
            analysis_result['overall_risk'] = 'CRITICAL'
        elif risk_score >= 8:
            analysis_result['overall_risk'] = 'HIGH'
        elif risk_score >= 3:
            analysis_result['overall_risk'] = 'MEDIUM'
        else:
            analysis_result['overall_risk'] = 'LOW'
        
        # Display results
        print(f"   📊 Overall Risk: {analysis_result['overall_risk']}")
        print(f"   🔍 Vulnerabilities Found: {len(analysis_result['vulnerabilities'])}")
        print(f"   ⚠️  Concentration Risks: {len(analysis_result['concentration_risks'])}")
        print(f"   🚨 Deployment Risks: {len(analysis_result['deployment_risks'])}")
        print(f"   💡 Recommendations: {len(analysis_result['recommendations'])}")
        
        # Show key findings
        if analysis_result['vulnerabilities']:
            print("   🔍 Key Vulnerabilities:")
            for vuln in analysis_result['vulnerabilities'][:3]:  # Show top 3
                print(f"      - {vuln['type'].upper()}: {vuln['description']}")
        
        if analysis_result['concentration_risks']:
            print("   ⚠️  Concentration Risks:")
            for risk in analysis_result['concentration_risks']:
                print(f"      - {risk['type'].upper()}: {risk['description']}")
        
        if analysis_result['deployment_risks']:
            print("   🚨 Deployment Risks:")
            for risk in analysis_result['deployment_risks']:
                print(f"      - {risk['type'].upper()}: {risk['description']}")
        
        if analysis_result['recommendations']:
            print("   💡 Top Recommendations:")
            for rec in analysis_result['recommendations'][:3]:  # Show top 3
                print(f"      - {rec}")
        
        print()
    
    print("✅ Defensive analysis tests completed!\n")

def run_tests():
    print("=== Running Defensive A1 System Tests ===\n")
    
    # Test defensive analysis capabilities
    run_defensive_analysis_tests()
    
    # Test enhanced vs original functionality
    run_enhanced_tests()
    
    # Run original basic tests for comparison
    print("\n=== Original Basic Tests (for comparison) ===")
    run_basic_tests()

def run_enhanced_tests():
    """Test the enhanced realistic mock implementations"""
    print("🔍 Testing Enhanced Mock Implementations...")
    
    agent = A1DefensiveAgent(MockLLM())
    
    # Register enhanced tools
    fetcher = SourceCodeFetcher("enhanced_fetcher")
    agent.register_tool("fetcher", fetcher)
    
    param_tool = ConstructorParameterTool("enhanced_params")
    agent.register_tool("params", param_tool)
    
    # Register enhanced StateReaderTool
    state_tool = StateReaderTool("enhanced_state_reader")
    agent.register_tool("state", state_tool)
    
    print(f"✅ Enhanced tools registered: {list(agent.tools.keys())}\n")
    
    # Test realistic contract scenarios
    test_contracts = [
        ("0x123", "VulnerableDeFiPool", 17892350),
        ("0x456", "TransparentUpgradeableProxy", 17892350), 
        ("0x789", "RealisticToken", 17892350),
        ("0x999", "Unknown Contract", 17892350)  # Test error case
    ]
    
    # Also test later blocks to see state evolution
    later_test_contracts = [
        ("0x123", "VulnerableDeFiPool (Later)", 17900000),
        ("0x789", "RealisticToken (Later)", 18000000),
    ]
    
    for address, name, block in test_contracts:
        print(f"📋 Testing {name} ({address})...")
        test_contract_analysis(agent, address, block)
        print()
    
    # Test state evolution over time
    print("🕐 Testing State Evolution Over Time...")
    for address, name, block in later_test_contracts:
        print(f"📋 Testing {name} at block {block}...")
        test_contract_analysis(agent, address, block)
        print()
    
    # Test historical block edge cases
    print("📅 Testing Historical Block Analysis...")
    test_historical_blocks(agent)
    
    # Test full agent workflow
    print("🤖 Testing Full Agent Workflow...")
    test_agent_workflow(agent)

def test_contract_analysis(agent, address, block):
    """Test comprehensive contract analysis"""
    
    # Test SourceCodeFetcher
    print(f"  🔍 Fetching source code...")
    fetch_result = agent.tools['fetcher'].execute("ethereum", address, block)
    if fetch_result["status"] == "success":
        print(f"    ✅ Source retrieved: {len(fetch_result['source_code'])} chars")
        print(f"    📊 Compiler: {fetch_result['compiler_version']}")
        if fetch_result.get('is_proxy'):
            print(f"    🔗 Proxy detected, implementation: {fetch_result['implementation_address']}")
    else:
        print(f"    ❌ Error: {fetch_result['error']}")
    
    # Test ConstructorParameterTool  
    print(f"  🏗️  Analyzing constructor parameters...")
    param_result = agent.tools['params'].execute("ethereum", address, block)
    if param_result["status"] == "success":
        params = param_result["parameters"]
        if params:
            print(f"    ✅ Parameters found: {list(params.keys())}")
            for key, value in params.items():
                print(f"      • {key}: {value}")
        else:
            print(f"    ℹ️  No constructor parameters")
        
        # Show security analysis
        analysis = param_result["analysis"]
        print(f"    🛡️  Security Risk: {analysis['risk_level'].upper()}")
        for finding in analysis["findings"]:
            print(f"      • {finding}")
            
        print(f"    ⛽ Gas used: {param_result['gas_used']:,}")
        print(f"    👤 Deployer: {param_result['deployer_address']}")
    else:
        print(f"    ❌ Error: {param_result['error']}")
    
    # Test Enhanced StateReaderTool
    print(f"  📊 Reading contract state...")
    state_result = agent.tools['state'].execute("ethereum", address, block)
    if state_result["status"] == "success":
        state = state_result["state"]
        print(f"    ✅ State retrieved from block {state_result['queried_block']}")
        print(f"    🔧 Available functions: {len(state_result['available_functions'])} functions")
        
        # Show key state information
        if "totalSupply" in state:
            supply = int(state["totalSupply"]) / 10**18
            print(f"    💰 Total Supply: {supply:,.0f} tokens")
        
        if "balances" in state and state["balances"]:
            print(f"    👥 Token holders: {len(state['balances'])}")
            
        if "contract_balance" in state:
            eth_balance = int(state["contract_balance"]) / 10**18
            print(f"    💎 Contract ETH: {eth_balance:.2f} ETH")
        
        # Show security analysis
        analysis = state_result["state_analysis"]
        print(f"    🛡️  Concentration Risk: {analysis['concentration_risk'].upper()}")
        for finding in analysis["findings"]:
            print(f"      • {finding}")
        
        # Show balance distribution
        distribution = state_result["balance_distribution"]
        if distribution.get("distribution") == "analyzed":
            print(f"    📈 Top holder: {distribution['top_holder_percentage']:.1f}% of supply")
        
        # Show risk indicators
        risks = state_result["risk_indicators"]
        if risks:
            print(f"    ⚠️  Risk indicators:")
            for risk in risks:
                print(f"      • {risk}")
                
    else:
        print(f"    ❌ Error: {state_result['error']}")

def test_historical_blocks(agent):
    """Test edge cases with historical block numbers"""
    print("  📅 Testing block before deployment (should fail)...")
    result = agent.tools['params'].execute("ethereum", "0x123", 17892000)  # Before deployment
    if result["status"] == "error":
        print(f"    ✅ Correctly rejected: {result['error']}")
    else:
        print(f"    ❌ Should have failed but got: {result}")
        
    print("  📅 Testing block after deployment (should succeed)...")
    result = agent.tools['params'].execute("ethereum", "0x123", 18000000)  # After deployment
    if result["status"] == "success":
        print(f"    ✅ Correctly accepted at block {result['deployment_block']}")
    else:
        print(f"    ❌ Should have succeeded: {result}")

def test_agent_workflow(agent):
    """Test the full A1Agent workflow with enhanced tools"""
    print("  🔄 Running complete agent analysis workflow...")
    
    try:
        # This will test the iterative tool selection with enhanced data
        result = agent.execute("ethereum", "0x456", 17892350)  # Test proxy contract
        
        print(f"    📊 Agent workflow result: {result['status']}")
        if result.get('message'):
            print(f"    💬 Message: {result['message']}")
            
        # The agent should have used tools and generated history
        print(f"    ✅ Agent workflow completed")
        
    except Exception as e:
        print(f"    ❌ Agent workflow failed: {str(e)}")

def run_basic_tests():
    """Run basic tests with minimal output for comparison"""
    agent = A1DefensiveAgent(MockLLM())
    
    # Register basic tools (these still have original mock implementations)
    dummy_tool = DummyTool("test_tool")
    agent.register_tool("dummy", dummy_tool)
    
    state_tool = StateReaderTool("state_reader")
    agent.register_tool("state", state_tool)
    
    sanitizer_tool = CodeSanitizerTool("code_sanitizer")
    agent.register_tool("sanitizer", sanitizer_tool)
    
    execution_tool = ConcreteExecutionTool("execution_tool")
    agent.register_tool("execution", execution_tool)
    
    revenue_tool = RevenueNormalizerTool("revenue_tool")
    agent.register_tool("revenue", revenue_tool)
    
    print(f"Basic tools registered: {list(agent.tools.keys())}")
    
    # Test basic tool execution
    result = agent.tools['dummy'].execute()
    print(f"Dummy tool: {result}")
    
    state_result = agent.tools['state'].execute("ethereum", "0x123", 12345)
    print(f"State tool: {state_result}")
    
    print("Basic tests completed.")

# Add a main execution block
if __name__ == "__main__":
    run_tests()
import streamlit as st
from web3 import Web3
import time

# Monad public RPC (you can swap this if one flakes)
# Good options: "https://rpc.monad.xyz", "https://monad-mainnet.gateway.tatum.io", "https://rpc1.monad.xyz"
RPC_URL = "https://rpc.monad.xyz"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Your contracts
contracts = {
    "AgentFactory": "0x4763F996547F54BC6eA834746B9fe4d250FabEBA",
    "AiCoinflipMON": "0xf01dfcA848a37B76025fc416d2b681c5aa057544",
    "AiGuardPrison": "0x6Ac2752De7eD1E8C62A08FC6f722be34a242Df1D"
}

st.set_page_config(page_title="Monad AI Projects Dashboard", page_icon="🔗", layout="wide")
st.title("🔗 Live Dashboard: Monad AI Projects")
st.markdown("Real-time MON balances and contract status. Refreshes every 10s. Data from Monad mainnet.")

if not w3.is_connected():
    st.error("❌ Unable to connect to Monad RPC. Try refreshing or check network status.")
    st.stop()

# Dashboard content
for name, address in contracts.items():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"**{name}**")
        st.code(address)
        
        # MON Balance (for all contracts)
        try:
            balance_wei = w3.eth.get_balance(address)
            balance_mon = w3.from_wei(balance_wei, "ether")
            st.metric("MON Balance", f"{balance_mon:,.4f}")
        except Exception as e:
            st.warning(f"Could not fetch MON balance: {str(e)}")
        
        # Custom metrics per contract
        if name == "AiCoinflipMON":
            try:
                # Minimal ABI just for totalBets()
                coinflip_abi = [
                    {
                        "inputs": [],
                        "name": "totalBets",
                        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                        "stateMutability": "view",
                        "type": "function"
                    }
                ]
                contract = w3.eth.contract(address=Web3.to_checksum_address(address), abi=coinflip_abi)
                total_flips = contract.functions.totalBets().call()
                st.metric("Number of Flips", total_flips)
            except Exception as e:
                st.warning(f"Could not fetch Number of Flips: {str(e)}")
        
        elif name == "AgentFactory":
            st.metric("Agents Deployed", "Event-based count")
            st.caption(
                "[View AgentDeployed events on Monadscan →](https://monadscan.com/address/"
                "0x4763F996547F54BC6eA834746B9fe4d250FabEBA#events)"
            )
        
        elif name == "AiGuardPrison":
            st.metric("Agents in Prison", "Event-based count")
            st.caption(
                "[View Jailed events on Monadscan →](https://monadscan.com/address/"
                "0x6Ac2752De7eD1E8C62A08FC6f722be34a242Df1D#events)"
            )
        
        # Contract deployment check
        try:
            code = w3.eth.get_code(address)
            deployed = len(code) > 0
            if deployed:
                st.success("✅ Contract Deployed")
            else:
                st.error("❌ No Code (not deployed)")
        except Exception as e:
            st.warning(f"Could not check deployment status: {str(e)}")
    
    with col2:
        st.markdown(f"[View on Monadscan](https://monadscan.com/address/{address})")

# Auto-refresh every 10 seconds
time.sleep(10)
st.rerun()

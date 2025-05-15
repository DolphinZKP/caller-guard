"""Main Streamlit application for ZK Caller Verification."""

import os
import sys
import logging
import streamlit as st
import time
from datetime import datetime
import uuid
import math
import streamlit.components.v1 as components

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.blockchain import get_blockchain_client
from app.db.base import get_db
from app.db.models.employee import Employee
from app.db.models.blockchain import BlockchainIdentity, AuditLog, AuditLogAction
from app.utils.crypto import decrypt, encrypt, generate_numeric_hash

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize blockchain client
blockchain_client = get_blockchain_client()

# Main app configuration
st.set_page_config(
    page_title="ZK Caller Verification", 
    page_icon="📞",
    layout="wide"
)

# Apply custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .agent-card {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .success-card {
        background-color: #f0fff0;
        border: 1px solid #009900;
        border-radius: 5px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .verification-code {
        font-size: 2.5rem;
        font-weight: bold;
        letter-spacing: 0.25rem;
        color: #1E3A8A;
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        margin: 1rem 0;
        font-family: monospace;
    }
    .verification-timer {
        text-align: center;
        font-size: 1rem;
        color: #4B5563;
        margin-bottom: 1rem;
    }
    .nav-pills {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
    }
    .nav-pill {
        margin: 0 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        cursor: pointer;
        text-align: center;
        font-weight: bold;
    }
    .nav-pill.active {
        background-color: #1E3A8A;
        color: white;
    }
    .nav-pill:not(.active) {
        background-color: #F3F4F6;
        color: #4B5563;
    }
    .status-badge {
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    .status-active {
        background-color: #DFF0D8;
        color: #3C763D;
    }
    .status-inactive {
        background-color: #F2DEDE;
        color: #A94442;
    }
    .status-pending {
        background-color: #FCF8E3;
        color: #8A6D3B;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to create audit logs safely
def create_audit_log(db, action, resource_type=None, resource_id=None, details=None):
    """Create an audit log entry safely without user_id to avoid foreign key issues"""
    try:
        # Use a separate transaction that can fail independently
        # This ensures the main transaction succeeds even if logging fails
        with get_db() as log_db:
            log_entry = AuditLog(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                # Explicitly set both user_id and user-related fields to None
                user_id=None,
                ip_address=None,
                user_agent=None,
                details=details
            )
            log_db.add(log_entry)
            log_db.commit()
        return True
    except Exception as e:
        logger.error(f"Error creating audit log: {e}")
        # Don't let audit logging failures affect the main operations
        return False

# Session state initialization
if 'enable_success' not in st.session_state:
    st.session_state.enable_success = False

if 'enable_result' not in st.session_state:
    st.session_state.enable_result = None

if 'current_page' not in st.session_state:
    st.session_state.current_page = "HR Admin"

if 'selected_agent_id' not in st.session_state:
    st.session_state.selected_agent_id = None

# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────
st.title("📞 ZK Caller Verification System - OKO Bank")

# Navigation menu
col1, col2, col3 = st.columns(3)
with col1:
    hr_active = "active" if st.session_state.current_page == "HR Admin" else ""
    if st.button("🧑‍💼 HR Admin", key="hr_admin_btn", use_container_width=True):
        st.session_state.current_page = "HR Admin"
        st.rerun()
with col3:
    agent_dash_active = "active" if st.session_state.current_page == "Agent Dashboard" else ""
    if st.button("👨‍💼 Agent Dashboard", key="agent_dashboard_btn", use_container_width=True):
        st.session_state.current_page = "Agent Dashboard"
        st.rerun()
with col2:
    agent_mgmt_active = "active" if st.session_state.current_page == "Agent Management" else ""
    if st.button("🔑 Agent Management", key="agent_management_btn", use_container_width=True):
        st.session_state.current_page = "Agent Management"
        st.rerun()

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# Render current page
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.current_page == "HR Admin":
    st.header("🧑‍💼 HR Admin")
    st.write("Enable call center employees as verified agents by minting their blockchain identity badges")
    
    # Get employee list
    with get_db() as db:
        # Get employees who don't have blockchain identities yet
        employees = db.query(Employee).join(
            BlockchainIdentity,
            Employee.id == BlockchainIdentity.employee_id,
            isouter=True
        ).filter(
            BlockchainIdentity.id == None
        ).all()
        
        # Format options for dropdown
        employee_options = [
            f"{e.rep_id} – {e.last_name}, {e.first_name} ({e.username})" 
            for e in employees
        ]
        
    if not employee_options:
        st.info("All employees have been enabled as agents. No more employees to enable.")
    else:
        # Employee selection and enablement
        if not st.session_state.enable_success:
            st.markdown("### Select Employee to Enable")
            selected = st.selectbox("Choose an employee to enable as an agent", employee_options)
            
            if selected:
                # Get the employee from the selection
                rep_id = selected.split(" – ")[0]
                
                with get_db() as db:
                    employee = db.query(Employee).filter(Employee.rep_id == rep_id).first()
                    
                    if employee:
                        # Display employee details
                        st.markdown("### Employee Details")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Name:** {employee.first_name} {employee.last_name}")
                            st.markdown(f"**Username:** {employee.username}")
                        
                        with col2:
                            st.markdown(f"**Rep ID:** {employee.rep_id}")
                            st.markdown(f"**Department:** {employee.department}")
                        
                        # Permissions section
                        st.markdown("### Permissions")
                        default_permissions = employee.permissions
                        
                        # Display permissions as read-only with emojis
                        col1, col2 = st.columns(2)
                        with col1:
                            can_open = default_permissions.get('can_open_acc', False)
                            emoji = "✅" if can_open else "❌"
                            st.markdown(f"**Can Open Accounts:** {emoji}", unsafe_allow_html=True)
                        with col2:
                            can_pay = default_permissions.get('can_take_pay', False)
                            emoji = "✅" if can_pay else "❌"
                            st.markdown(f"**Can Take Payments:** {emoji}", unsafe_allow_html=True)
                        
                        # Button to enable the employee as an agent
                        if st.button("Mint Badge and Enable Agent", use_container_width=True):
                            with st.spinner("Generating blockchain identity and minting badge..."):
                                with get_db() as db:
                                    employee = db.query(Employee).filter(Employee.rep_id == rep_id).first()
                                    
                                    if employee:
                                        # Flag to control execution flow
                                        proceed_with_enable = True
                                        
                                        # Generate seed for OTP
                                        seed = int.from_bytes(os.urandom(4), 'big')
                                        logger.info(f"Generated seed for {employee.rep_id}: {seed}")
                                        
                                        # Generate short ID from rep_id
                                        short_id = generate_numeric_hash(employee.rep_id, 2)
                                        logger.info(f"Generated short ID for {employee.rep_id}: {short_id}")
                                        
                                        # Log action
                                        logger.info(f"Minting blockchain badge for employee: {employee.first_name} {employee.last_name}")
                                        
                                        # Create blockchain badge
                                        result = blockchain_client.mint_badge(
                                            first_name=employee.first_name,
                                            last_name=employee.last_name,
                                            username=employee.username,
                                            rep_id=employee.rep_id,
                                            org_id=settings.ORG_ID,
                                            short_id=short_id,
                                            seed=seed,
                                            digits=settings.DEFAULT_OTP_DIGITS,
                                            permissions=employee.permissions
                                        )
                                        
                                        # Encrypt the sensitive data
                                        try:
                                            # Encrypt the seed properly
                                            seed_str = str(seed)
                                            encrypted_seed = encrypt(seed_str)
                                            logger.info(f"Encrypted seed: {encrypted_seed[:20]}...")
                                            
                                            # Encrypt private key
                                            encrypted_private_key = encrypt(result["private_key"])
                                            logger.info(f"Encrypted private key: {encrypted_private_key[:20]}...")
                                            
                                            # Encrypt view key
                                            encrypted_view_key = encrypt(result["view_key"])
                                            logger.info(f"Encrypted view key: {encrypted_view_key[:20]}...")
                                            
                                            # Create blockchain identity in database
                                            identity = BlockchainIdentity(
                                                employee_id=employee.id,
                                                aleo_address=result["aleo_address"],
                                                private_key_encrypted=encrypted_private_key,
                                                view_key_encrypted=encrypted_view_key,
                                                short_id=short_id,
                                                seed=encrypted_seed,
                                                badge_ciphertext=result["badge_ciphertext"],
                                                otp_digits=settings.DEFAULT_OTP_DIGITS,
                                                is_active=True
                                            )
                                            
                                            # Add and commit the identity first to ensure it's saved
                                            # even if audit logging fails
                                            db.add(identity)
                                            db.commit()
                                            logger.info(f"Successfully saved blockchain identity for {employee.rep_id}")
                                            
                                            # Now log the action separately - if this fails, it won't affect
                                            # the main transaction that already completed
                                            create_audit_log(
                                                db=db,
                                                action=AuditLogAction.AGENT_ENABLE,
                                                resource_type="employee",
                                                resource_id=str(employee.id),
                                                details={
                                                    "rep_id": employee.rep_id,
                                                    "aleo_address": result["aleo_address"]
                                                }
                                            )
                                            
                                            # Update session state
                                            st.session_state.enable_success = True
                                            st.session_state.enable_result = {
                                                'success': True,
                                                'employee': {
                                                    'name': f"{employee.first_name} {employee.last_name}",
                                                    'rep_id': employee.rep_id
                                                },
                                                'blockchain': {
                                                    'address': result["aleo_address"]
                                                }
                                            }
                                            
                                            logger.info(f"Successfully enabled agent: {employee.rep_id}")
                                            
                                        except Exception as e:
                                            logger.error(f"Error encrypting sensitive data: {e}")
                                            st.error("Error securing agent data. Please try again or contact system administrator.")
                                            # Don't continue execution
                                            proceed_with_enable = False
                                        
                                        # Only reload if successful
                                        if proceed_with_enable:
                                            # Refresh
                                            st.rerun()
                                    else:
                                        st.error(f"Failed to enable agent: Employee not found: {rep_id}")
                    else:
                        st.error(f"Employee not found: {rep_id}")
        else:
            # Success message after enabling
            st.markdown("### Agent Successfully Enabled ✅")
            result = st.session_state.enable_result
            
            st.markdown(f"""
            <div class="success-card">
                <h3>Agent Badge Minted!</h3>
                <p><strong>Employee:</strong> {result['employee']['name']}</p>
                <p><strong>Rep ID:</strong> {result['employee']['rep_id']}</p>
                <p><strong>Blockchain Address:</strong> {result['blockchain']['address']}</p>
                <p>The employee can now generate one-time verification codes for caller authentication.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Reset success flag when user wants to enable another agent
            if st.button("Enable Another Agent"):
                st.session_state.enable_success = False
                st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# Agent Dashboard Tab
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.current_page == "Agent Dashboard":
    st.header("👨‍💼 Agent Dashboard")
    st.write("Generate your one-time verification code for caller authentication")
    
    # Add an invisible refresh element to redraw the page periodically and check OTP expiry
    # This refreshes every 3 seconds without disrupting the user
    if 'refresh_counter' not in st.session_state:
        st.session_state.refresh_counter = 0
    
    # Increment counter and get a new element key each time
    st.session_state.refresh_counter += 1
    refresh_key = f"refresh_{st.session_state.refresh_counter}"
    
    # Add an invisible component that refreshes every 3 seconds
    # This ensures we consistently check for code expiry without JS redirects
    st.empty().markdown(f"""
    <div style="display: none;" id="{refresh_key}"></div>
    <script>
        function refreshDiv() {{
            const refreshEl = document.getElementById("{refresh_key}");
            if (refreshEl) {{
                refreshEl.innerText = new Date().toISOString();
            }}
        }}
        setInterval(refreshDiv, 3000);
    </script>
    """, unsafe_allow_html=True)
    
    # Get active agents for dropdown
    with get_db() as db:
        agents = db.query(Employee).join(
            BlockchainIdentity,
            Employee.id == BlockchainIdentity.employee_id
        ).filter(
            BlockchainIdentity.is_active == True
        ).all()
        
        # Format options for dropdown
        agent_options = [
            f"{a.rep_id} – {a.last_name}, {a.first_name} ({a.username})" 
            for a in agents
        ]
    
    if not agent_options:
        st.info("No active agents found. Please enable an agent first.")
    else:
        selected = st.selectbox("Select Your Identity", agent_options, key="agent_select")
        
        # Track last code generation time and rep_id in session state
        if 'last_otp_time' not in st.session_state:
            st.session_state.last_otp_time = None
        if 'last_otp_rep_id' not in st.session_state:
            st.session_state.last_otp_rep_id = None
        if 'last_otp_code' not in st.session_state:
            st.session_state.last_otp_code = None
        if 'last_otp_time_window' not in st.session_state:
            st.session_state.last_otp_time_window = None
 
        # If agent selection changes, reset last OTP
        if selected and st.session_state.last_otp_rep_id != selected:
            st.session_state.last_otp_time = None
            st.session_state.last_otp_code = None
            st.session_state.last_otp_time_window = None
            st.session_state.last_otp_rep_id = selected

        rep_id = selected.split(" – ")[0] if selected else None

        # Calculate current time window
        current_time = time.time()
        time_window = int(current_time // settings.OTP_WINDOW_SIZE)
        window_start = math.floor(current_time / settings.OTP_WINDOW_SIZE) * settings.OTP_WINDOW_SIZE
        initial_remaining = int(settings.OTP_WINDOW_SIZE - (current_time - window_start))

        # Initialize generate_button_clicked variable
        generate_button_clicked = False
        
        # Check if we should force regeneration due to timer expiry flag
        if st.session_state.get('force_otp_regeneration_due_to_timer'):
            generate_button_clicked = True
            st.session_state.force_otp_regeneration_due_to_timer = False
        
        # Auto-generate code if:
        # - No code generated yet for this rep_id, or
        # - The time window has changed (timer expired)
        # - OR exactly 60 seconds have passed since last code generation
        auto_generate = False
        if selected:
            # Check if it's been 60 seconds since the last OTP generation
            force_regenerate_due_to_time = False
            if st.session_state.last_otp_time is not None:
                time_since_last_generation = current_time - st.session_state.last_otp_time
                if time_since_last_generation >= settings.OTP_WINDOW_SIZE:
                    logger.info(f"60 seconds passed since last code generation ({time_since_last_generation:.2f}s). Auto-regenerating.")
                    force_regenerate_due_to_time = True
                    # Set as if button was clicked to get fresh code
                    generate_button_clicked = True
            
            # Standard auto-generate conditions
            if (st.session_state.last_otp_time_window != time_window or
                st.session_state.last_otp_code is None or
                force_regenerate_due_to_time):
                auto_generate = True
                
        # Add a click counter to session state
        if 'click_counter' not in st.session_state:
            st.session_state.click_counter = 0
            
        # Store button click and increment counter (this is the key to ensuring we detect every click)    
        if not generate_button_clicked:  # Only check the button if we haven't already set it
            generate_button_clicked = st.button("Generate One-Time Verification Code", key="gen_otp")
        
        # If button is clicked, increment counter and reset OTP state
        if generate_button_clicked:
            st.session_state.click_counter += 1
            st.session_state.last_otp_time = None
            st.session_state.last_otp_code = None
            st.session_state.last_otp_time_window = None

        if selected and (generate_button_clicked or auto_generate):
            with st.spinner("Generating verification code..."):
                try:
                    with get_db() as db:
                        # Get agent data from database
                        agent = db.query(BlockchainIdentity).join(
                            Employee,
                            Employee.id == BlockchainIdentity.employee_id
                        ).filter(
                            Employee.rep_id == rep_id
                        ).first()
                        
                        if agent:
                            # Flag to track if we should continue with OTP generation
                            proceed_with_otp = True
                            
                            # Get seed from database and handle it properly
                            try:
                                # Debug info
                                logger.info(f"Seed from database: {type(agent.seed)} - {agent.seed[:20] if isinstance(agent.seed, str) else 'not string'}")
                                
                                # Decrypt the seed
                                decrypted_seed = decrypt(agent.seed)
                                logger.info(f"Decrypted seed type: {type(decrypted_seed)}, value: {decrypted_seed}")
                                
                                # Convert to integer (handle both string and int types)
                                if isinstance(decrypted_seed, str):
                                    seed = int(decrypted_seed)
                                else:
                                    seed = int(decrypted_seed)
                                    
                                logger.info(f"Successfully decrypted seed for agent {rep_id}: {seed}")
                            
                            except Exception as e:
                                logger.error(f"Error decrypting seed: {e}")
                                st.error("Error accessing secure data. Please contact system administrator. You may need to regenerate your agent identity.")
                                proceed_with_otp = False
                            
                            # Only continue if seed decryption was successful
                            if proceed_with_otp:
                                # Get rep_id numeric value
                                rep_id_numeric = agent.short_id
                                logger.info(f"Short ID: {rep_id_numeric}")
                                
                                # Generate OTP with better error handling
                                try:
                                    # Manual OTP generation (without blockchain client)
                                    # If button is clicked, add extra modification to the time to ensure a new code
                                    if generate_button_clicked:
                                        # Add the current microseconds to ensure a different seed value
                                        time_bytes = (time_window + int(time.time() * 1000000) % 1000).to_bytes(8, byteorder='big')
                                        logger.info("Button clicked, generating fresh code with modified time")
                                    else:
                                        time_bytes = time_window.to_bytes(8, byteorder='big')
                                        
                                    seed_bytes = seed.to_bytes(8, byteorder='big')
                                    message = time_bytes + rep_id_numeric.to_bytes(2, byteorder='big')
                                    
                                    # Generate HMAC-SHA1
                                    import hmac
                                    import hashlib
                                    hmac_hash = hmac.new(seed_bytes, message, hashlib.sha1).digest()
                                    
                                    # Extract 4 bytes from the hash
                                    offset = hmac_hash[-1] & 0x0F
                                    code_bytes = hmac_hash[offset:offset+4]
                                    
                                    # Convert to code
                                    code_int = int.from_bytes(code_bytes, byteorder='big') & 0x7FFFFFFF
                                    code = code_int % (10 ** 6)  # 6-digit code
                                    
                                    # Format with leading zeros
                                    code_str = f"{code:06d}"
                                    
                                    logger.info(f"Successfully generated OTP: {code_str}")
                                except Exception as e:
                                    logger.error(f"Error in manual OTP generation: {e}")
                                    st.error("Failed to generate verification code. Please try again.")
                                    proceed_with_otp = False
                                
                                # Only continue if OTP generation was successful
                                if proceed_with_otp:
                                    # Log the OTP generation using our safe helper
                                    try:
                                        create_audit_log(
                                            db=db,
                                            action=AuditLogAction.AGENT_OTP_GENERATE,
                                            resource_type="agent",
                                            resource_id=str(agent.id),
                                            details={
                                                "time_window": time_window,
                                                "digits": agent.otp_digits
                                            }
                                        )
                                    except Exception as e:
                                        logger.error(f"Error creating audit log for OTP generation: {e}")
                                        # Continue without failing if just the audit log fails
                                    
                                    # Store code and time in session state
                                    st.session_state.last_otp_time = current_time
                                    st.session_state.last_otp_code = code_str
                                    st.session_state.last_otp_time_window = time_window
                                    st.session_state.last_otp_rep_id = selected
                                    
                                    # Generate a unique ID for this timer instance
                                    countdown_time = time.time()
                                    unique_timer_id = str(int(countdown_time * 1000))
                                    
                                    # Display the code
                                    st.markdown(f"<div class='verification-code'>{code_str}</div>", unsafe_allow_html=True)
                                    
                                    # Always use a full time window for the timer initially
                                    initial_remaining = settings.OTP_WINDOW_SIZE
                                    logger.info(f"Setting timer to full duration: {settings.OTP_WINDOW_SIZE} seconds (click #{st.session_state.click_counter})")
                                    
                                    # Add a beautiful, centered countdown timer with auto-refresh and unique ID
                                    countdown_html = f"""
                                    <div style='text-align:center; margin-top:1.5rem;' id='timer-container-{unique_timer_id}'>
                                        <span style='font-size:1.2rem; color:#4B5563;'>Code valid for</span><br>
                                        <span id='countdown-{unique_timer_id}' style='font-size:3.5rem; font-weight:bold; color:#1E3A8A; letter-spacing:0.1em;'>{initial_remaining}</span>
                                        <span style='font-size:1.2rem; color:#4B5563;'>seconds</span>
                                    </div>
                                    <script>
                                        // Make sure we're counting from the full initial time
                                        let timeLeft_{unique_timer_id} = {initial_remaining};
                                        const countdownEl_{unique_timer_id} = document.getElementById('countdown-{unique_timer_id}');
                                        const interval_{unique_timer_id} = setInterval(() => {{
                                            timeLeft_{unique_timer_id}--;
                                            
                                            if (timeLeft_{unique_timer_id} < 0) {{
                                                clearInterval(interval_{unique_timer_id});
                                                countdownEl_{unique_timer_id}.innerHTML = '0';
                                                countdownEl_{unique_timer_id}.style.color = '#dc2626';
                                                // NO PAGE RELOAD - let Python handle regeneration
                                            }} else {{
                                                countdownEl_{unique_timer_id}.innerHTML = timeLeft_{unique_timer_id};
                                            }}
                                        }}, 1000);
                                    </script>
                                    """
                                    components.html(countdown_html, height=120)
                                    
                                    # Display customer instructions
                                    st.markdown("### Instructions for Customer")
                                    
                                    # Get employee data to display name
                                    employee = db.query(Employee).filter(Employee.id == agent.employee_id).first()
                                    agent_name = f"{employee.first_name} {employee.last_name}"
                                    
                                    st.markdown(f"""
                                    #### Guide the customer through verification:

                                    1. **Open the authenticator app**
                                       * Select "OKO Bank" from institution list
                                    
                                    2. **Enter verification details**
                                       * RepID: `{employee.rep_id}`
                                       * Code: `{code_str}` (shown above)
                                    
                                    3. **Complete verification**
                                       * Click "Submit"
                                    
                                    4. **Confirmation**
                                       * The customer will see {agent_name}'s verified identity
                                       * They can view what {employee.first_name} is authorized to do
                                    """)
                        else:
                            st.error(f"Agent not found with ID: {rep_id}")
                except Exception as e:
                    st.error(f"Error generating code: {str(e)}")
                    logger.error(f"Error generating OTP: {e}")
        elif selected and st.session_state.last_otp_code:
            # Display the last generated code and timer if not expired
            code_str = st.session_state.last_otp_code
            
            # Generate a unique ID for this timer instance
            unique_timer_id = str(int(time.time() * 1000))
            
            # Display the code
            st.markdown(f"<div class='verification-code'>{code_str}</div>", unsafe_allow_html=True)
            
            # Calculate remaining time for existing code
            current_time = time.time()
            next_window_time = (math.floor(st.session_state.last_otp_time_window + 1) * settings.OTP_WINDOW_SIZE)
            initial_remaining = int(max(0, next_window_time - current_time))
            
            # Add a beautiful, centered countdown timer with auto-refresh and unique ID
            countdown_html = f"""
            <div style='text-align:center; margin-top:1.5rem;' id='timer-container-{unique_timer_id}'>
                <span style='font-size:1.2rem; color:#4B5563;'>Code valid for</span><br>
                <span id='countdown-{unique_timer_id}' style='font-size:3.5rem; font-weight:bold; color:#1E3A8A; letter-spacing:0.1em;'>{initial_remaining}</span>
                <span style='font-size:1.2rem; color:#4B5563;'>seconds</span>
            </div>
            <script>
                // Make sure we're counting from the full initial time
                let timeLeft_{unique_timer_id} = {initial_remaining};
                const countdownEl_{unique_timer_id} = document.getElementById('countdown-{unique_timer_id}');
                const interval_{unique_timer_id} = setInterval(() => {{
                    timeLeft_{unique_timer_id}--;
                    
                    if (timeLeft_{unique_timer_id} < 0) {{
                        clearInterval(interval_{unique_timer_id});
                        countdownEl_{unique_timer_id}.innerHTML = '0';
                        countdownEl_{unique_timer_id}.style.color = '#dc2626';
                        // NO PAGE RELOAD - let Python handle regeneration
                    }} else {{
                        countdownEl_{unique_timer_id}.innerHTML = timeLeft_{unique_timer_id};
                    }}
                }}, 1000);
            </script>
            """
            components.html(countdown_html, height=120)
            
            # Display customer instructions
            with get_db() as db:
                agent = db.query(BlockchainIdentity).join(
                    Employee,
                    Employee.id == BlockchainIdentity.employee_id
                ).filter(
                    Employee.rep_id == rep_id
                ).first()
                employee = db.query(Employee).filter(Employee.id == agent.employee_id).first() if agent else None
                agent_name = f"{employee.first_name} {employee.last_name}" if employee else ""
                st.markdown(f"""
                #### Guide the customer through verification:

                1. **Open the authenticator app**
                   * Select "OKO Bank" from institution list
                
                2. **Enter verification details**
                   * RepID: `{employee.rep_id if employee else ''}`
                   * Code: `{code_str}` (shown above)
                
                3. **Complete verification**
                   * Click "Submit"
                
                4. **Confirmation**
                   * You will see my verified identity
                   * They can view what I am authorized to do during the call.
                """)

# ─────────────────────────────────────────────────────────────────────────────
# Agent Management Tab
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.current_page == "Agent Management":
    st.header("🔑 Agent Management")
    st.write("Manage agent identities, revoke access, and view activity logs")
    
    # Add tabs for different views
    tab1, tab2 = st.tabs(["Enabled Agents", "All Employees"])
    
    # Get all employees and their blockchain status
    with get_db() as db:
        # Query all employees with left join to blockchain identities
        employee_data = db.query(
            Employee, 
            BlockchainIdentity
        ).outerjoin(
            BlockchainIdentity,
            Employee.id == BlockchainIdentity.employee_id
        ).all()
    
    # Tab 1: Enabled Agents
    with tab1:
        st.markdown("### Enabled Agents")
        
        # Filter to only show enabled agents
        enabled_agents = [(employee, blockchain_id) for employee, blockchain_id in employee_data 
                          if blockchain_id is not None and blockchain_id.is_active]
        
        if not enabled_agents:
            st.info("No enabled agents found. Use the HR Admin tab to enable agents.")
        else:
            # Create a table with columns
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1.5, 1.5])
            
            # Table headers
            col1.markdown("**Name**")
            col2.markdown("**Username / Rep ID**")
            col3.markdown("**Department**")
            col4.markdown("**Permissions**")
            col5.markdown("**Actions**")
            
            st.markdown("---")
            
            # Display each agent as a row
            for employee, blockchain_id in enabled_agents:
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1.5, 1.5])
                
                # Name column
                col1.write(f"{employee.last_name}, {employee.first_name}")
                
                # Username/Rep ID column
                col2.write(f"{employee.username} ({employee.rep_id})")
                
                # Department
                col3.write(f"{employee.department}")
                
                # Permissions column
                permissions = employee.permissions
                can_open = "✅" if permissions.get('can_open_acc', False) else "❌"
                can_pay = "✅" if permissions.get('can_take_pay', False) else "❌"
                col4.write(f"Open: {can_open} Pay: {can_pay}")
                
                # Actions column
                if st.session_state.selected_agent_id == employee.id:
                    if col5.button("Hide Details", key=f"hide_{employee.id}"):
                        st.session_state.selected_agent_id = None
                        st.rerun()
                else:
                    if col5.button("View Details", key=f"view_{employee.id}"):
                        st.session_state.selected_agent_id = employee.id
                        st.rerun()
                
                # Display details if this employee is selected
                if st.session_state.selected_agent_id == employee.id:
                    with st.expander("Agent Details", expanded=True):
                        # Display agent details in two columns
                        dcol1, dcol2 = st.columns(2)
                        with dcol1:
                            st.markdown(f"**Aleo Address:** `{blockchain_id.aleo_address[:15]}...`")
                            st.markdown(f"**OTP Digits:** {blockchain_id.otp_digits}")
                            st.markdown(f"**Enabled At:** {blockchain_id.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        with dcol2:
                            status = "✅ Active" if blockchain_id.is_active else "❌ Revoked"
                            st.markdown(f"**Status:** {status}", unsafe_allow_html=True)
                            if blockchain_id.revoked_at:
                                st.markdown(f"**Revoked At:** {blockchain_id.revoked_at.strftime('%Y-%m-%d %H:%M:%S')}")
                            st.markdown(f"**Position:** {employee.position}")
                        
                        # Actions based on current status
                        if blockchain_id.is_active:
                            if st.button("Revoke Agent Access", type="primary", key=f"revoke_{employee.id}"):
                                with st.spinner("Revoking agent access..."):
                                    with get_db() as db:
                                        # Refresh the identity data
                                        agent = db.query(BlockchainIdentity).filter(BlockchainIdentity.id == blockchain_id.id).first()
                                        
                                        # Call blockchain to revoke
                                        result = blockchain_client.revoke_badge(agent.badge_ciphertext)
                                        
                                        # Update database
                                        agent.is_active = False
                                        agent.revoked_at = datetime.utcnow()
                                        db.commit()  # Commit the changes first
                                        
                                        # Log the revocation using our safe helper
                                        create_audit_log(
                                            db=db,
                                            action=AuditLogAction.AGENT_REVOKE,
                                            resource_type="agent",
                                            resource_id=str(agent.id),
                                            details={
                                                "rep_id": employee.rep_id,
                                                "reason": "Admin revocation"
                                            }
                                        )
                                        
                                        st.success(f"Agent '{employee.first_name} {employee.last_name}' has been revoked")
                                        # Refresh the page
                                        time.sleep(2)
                                        st.rerun()
                        
                        # Recent Activity section
                        st.markdown("### Recent Activity")
                        with get_db() as db:
                            logs = db.query(AuditLog).filter(
                                AuditLog.resource_type == "agent",
                                AuditLog.resource_id == str(blockchain_id.id)
                            ).order_by(
                                AuditLog.timestamp.desc()
                            ).limit(5).all()
                            
                            if logs:
                                for log in logs:
                                    timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                                    st.markdown(f"**{timestamp}** - {log.action.value}")
                            else:
                                st.info("No recent activity found for this agent")
                    
                    st.markdown("---")
                else:
                    st.markdown("---")
    
    # Tab 2: All Employees
    with tab2:
        st.markdown("### All Employees")
        
        # Add search functionality
        search_query = st.text_input("🔍 Search by name, username, or Rep ID", key="employee_search")
        
        # Filter employees based on search query
        filtered_employees = employee_data
        if search_query:
            search_query = search_query.lower()
            filtered_employees = [
                (emp, bid) for emp, bid in employee_data
                if (search_query in emp.first_name.lower() or
                    search_query in emp.last_name.lower() or
                    search_query in emp.username.lower() or
                    search_query in emp.rep_id.lower())
            ]
        
        # Create a table with columns
        col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1.5, 1.5])
        
        # Table headers
        col1.markdown("**Name**")
        col2.markdown("**Username / Rep ID**")
        col3.markdown("**Department**")
        col4.markdown("**Status**")
        col5.markdown("**Actions**")
        
        st.markdown("---")
        
        if not filtered_employees:
            st.info("No employees found matching your search criteria.")
        else:
            # Display each employee as a row
            for employee, blockchain_id in filtered_employees:
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1.5, 1.5])
                
                # Name column
                col1.write(f"{employee.last_name}, {employee.first_name}")
                
                # Username/Rep ID column
                col2.write(f"{employee.username} ({employee.rep_id})")
                
                # Department
                col3.write(f"{employee.department}")
                
                # Status column with badge
                if blockchain_id is None:
                    col4.markdown("<span class='status-badge status-pending'>Not Enabled</span>", unsafe_allow_html=True)
                elif blockchain_id.is_active:
                    col4.markdown("<span class='status-badge status-active'>Active</span>", unsafe_allow_html=True)
                else:
                    col4.markdown("<span class='status-badge status-inactive'>Revoked</span>", unsafe_allow_html=True)
                
                # Actions column
                if blockchain_id is not None:
                    if st.session_state.selected_agent_id == employee.id:
                        if col5.button("Hide Details", key=f"hide_all_{employee.id}"):
                            st.session_state.selected_agent_id = None
                            st.rerun()
                    else:
                        if col5.button("View Details", key=f"view_all_{employee.id}"):
                            st.session_state.selected_agent_id = employee.id
                            st.rerun()
                else:
                    col5.write("Not enabled")
                
                # Display details if this employee is selected
                if st.session_state.selected_agent_id == employee.id and blockchain_id is not None:
                    with st.expander("Agent Details", expanded=True):
                        # Display agent details in two columns
                        dcol1, dcol2 = st.columns(2)
                        with dcol1:
                            st.markdown(f"**Aleo Address:** `{blockchain_id.aleo_address[:15]}...`")
                            st.markdown(f"**OTP Digits:** {blockchain_id.otp_digits}")
                            st.markdown(f"**Enabled At:** {blockchain_id.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        with dcol2:
                            status = "✅ Active" if blockchain_id.is_active else "❌ Revoked"
                            st.markdown(f"**Status:** {status}", unsafe_allow_html=True)
                            if blockchain_id.revoked_at:
                                st.markdown(f"**Revoked At:** {blockchain_id.revoked_at.strftime('%Y-%m-%d %H:%M:%S')}")
                            st.markdown(f"**Position:** {employee.position}")
                        
                        # Actions based on current status
                        if blockchain_id.is_active:
                            if st.button("Revoke Agent Access", type="primary", key=f"revoke_all_{employee.id}"):
                                with st.spinner("Revoking agent access..."):
                                    with get_db() as db:
                                        # Refresh the identity data
                                        agent = db.query(BlockchainIdentity).filter(BlockchainIdentity.id == blockchain_id.id).first()
                                        
                                        # Call blockchain to revoke
                                        result = blockchain_client.revoke_badge(agent.badge_ciphertext)
                                        
                                        # Update database
                                        agent.is_active = False
                                        agent.revoked_at = datetime.utcnow()
                                        db.commit()  # Commit the changes first
                                        
                                        # Log the revocation using our safe helper
                                        create_audit_log(
                                            db=db,
                                            action=AuditLogAction.AGENT_REVOKE,
                                            resource_type="agent",
                                            resource_id=str(agent.id),
                                            details={
                                                "rep_id": employee.rep_id,
                                                "reason": "Admin revocation"
                                            }
                                        )
                                        
                                        st.success(f"Agent '{employee.first_name} {employee.last_name}' has been revoked")
                                        # Refresh the page
                                        time.sleep(2)
                                        st.rerun()
                        else:
                            if st.button("Reactivate Agent", key=f"reactivate_all_{employee.id}"):
                                with st.spinner("Reactivating agent..."):
                                    with get_db() as db:
                                        # Refresh the identity data
                                        agent = db.query(BlockchainIdentity).filter(BlockchainIdentity.id == blockchain_id.id).first()
                                        
                                        # Update database
                                        agent.is_active = True
                                        agent.revoked_at = None
                                        db.commit()  # Commit the changes first
                                        
                                        # Log the reactivation using our safe helper
                                        create_audit_log(
                                            db=db,
                                            action=AuditLogAction.AGENT_ENABLE,
                                            resource_type="agent",
                                            resource_id=str(agent.id),
                                            details={
                                                "rep_id": employee.rep_id,
                                                "reason": "Admin reactivation"
                                            }
                                        )
                                        
                                        st.success(f"Agent '{employee.first_name} {employee.last_name}' has been reactivated")
                                        # Refresh the page
                                        time.sleep(2)
                                        st.rerun()
                        
                        # Recent Activity section
                        st.markdown("### Recent Activity")
                        with get_db() as db:
                            logs = db.query(AuditLog).filter(
                                AuditLog.resource_type == "agent",
                                AuditLog.resource_id == str(blockchain_id.id)
                            ).order_by(
                                AuditLog.timestamp.desc()
                            ).limit(5).all()
                            
                            if logs:
                                for log in logs:
                                    timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                                    st.markdown(f"**{timestamp}** - {log.action.value}")
                            else:
                                st.info("No recent activity found for this agent")
                    
                    st.markdown("---")
                else:
                    st.markdown("---")

# Footer
st.markdown("---")
st.markdown(f"ZK Caller Verification System v{settings.VERSION} | Demo Mode: {'Enabled' if settings.DEMO_MODE else 'Disabled'}")

# Main entry point
if __name__ == "__main__":
    # No redirect checks needed here, we'll handle everything in session state
    pass


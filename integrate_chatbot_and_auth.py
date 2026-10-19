import os
import shutil

html_path = os.path.join("aws", "agronex_dashboard", "index.html")
bak_path = html_path + ".bak"

# Always restore clean from bak if exists
if os.path.exists(bak_path):
    shutil.copyfile(bak_path, html_path)
else:
    shutil.copyfile(html_path, bak_path)

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. CSS to inject into </style>
auth_and_chat_css = """
    /* =========================================================================
       VERIFIED LOGIN & SIGN UP MODAL STYLES (§5.8)
       ========================================================================= */
    .auth-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(7, 13, 20, 0.88);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      z-index: 99999;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
      transition: opacity 0.4s ease, visibility 0.4s ease;
    }
    .auth-overlay.hidden {
      opacity: 0;
      visibility: hidden;
      pointer-events: none;
    }
    .auth-card {
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(56, 189, 248, 0.25);
      border-radius: 24px;
      width: 100%;
      max-width: 440px;
      padding: 32px 28px;
      box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.7), 0 0 35px rgba(16, 185, 129, 0.2);
      position: relative;
      animation: authSlideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes authSlideUp {
      from { opacity: 0; transform: translateY(24px) scale(0.96); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }
    .auth-header {
      text-align: center;
      margin-bottom: 24px;
    }
    .auth-logo {
      font-size: 38px;
      display: inline-block;
      margin-bottom: 8px;
      filter: drop-shadow(0 0 16px rgba(16, 185, 129, 0.5));
    }
    .auth-title {
      font-size: 22px;
      font-weight: 700;
      color: #f8fafc;
      letter-spacing: -0.3px;
    }
    .auth-subtitle {
      font-size: 13px;
      color: var(--text-muted);
      margin-top: 4px;
    }
    .auth-tabs {
      display: flex;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 4px;
      margin-bottom: 22px;
      border: 1px solid rgba(255, 255, 255, 0.06);
    }
    .auth-tab-btn {
      flex: 1;
      padding: 9px 0;
      font-size: 13.5px;
      font-weight: 600;
      background: transparent;
      border: none;
      color: var(--text-muted);
      border-radius: 9px;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .auth-tab-btn.active {
      background: rgba(16, 185, 129, 0.2);
      color: #10b981;
      border: 1px solid rgba(16, 185, 129, 0.4);
      box-shadow: 0 2px 10px rgba(16, 185, 129, 0.15);
    }
    .auth-form-group {
      margin-bottom: 16px;
    }
    .auth-label {
      display: block;
      font-size: 12.5px;
      font-weight: 600;
      color: #cbd5e1;
      margin-bottom: 6px;
    }
    .auth-input {
      width: 100%;
      background: rgba(10, 18, 30, 0.7);
      border: 1px solid rgba(56, 189, 248, 0.2);
      border-radius: 10px;
      padding: 11px 14px;
      color: #f8fafc;
      font-family: inherit;
      font-size: 14px;
      outline: none;
      transition: all 0.2s ease;
    }
    .auth-input:focus {
      border-color: #10b981;
      box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.18);
      background: rgba(10, 18, 30, 0.9);
    }
    .auth-msg {
      font-size: 12.5px;
      margin-top: 12px;
      padding: 8px 12px;
      border-radius: 8px;
      display: none;
      text-align: center;
    }
    .auth-msg.error {
      display: block;
      background: rgba(244, 63, 94, 0.15);
      color: #fda4af;
      border: 1px solid rgba(244, 63, 94, 0.3);
    }
    .auth-msg.success {
      display: block;
      background: rgba(16, 185, 129, 0.15);
      color: #6ee7b7;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .auth-submit-btn {
      width: 100%;
      margin-top: 8px;
      padding: 12px 0;
      font-size: 14.5px;
      font-weight: 700;
      border-radius: 12px;
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      color: #ffffff;
      border: none;
      cursor: pointer;
      transition: all 0.25s ease;
      box-shadow: 0 4px 16px rgba(16, 185, 129, 0.35);
    }
    .auth-submit-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 22px rgba(16, 185, 129, 0.45);
    }
    .auth-footer-hint {
      margin-top: 16px;
      font-size: 11.5px;
      color: var(--text-sub);
      text-align: center;
      line-height: 1.5;
    }

    /* =========================================================================
       KISAN MITRA MODERN AI CHATBOT STYLES (TRILINGUAL: EN / MR / HI)
       ========================================================================= */
    .kisan-fab {
      position: fixed;
      bottom: 26px;
      right: 26px;
      z-index: 9999;
      display: flex;
      align-items: center;
      cursor: pointer;
      user-select: none;
    }
    .kisan-avatar-btn {
      width: 64px;
      height: 64px;
      border-radius: 50%;
      background: linear-gradient(135deg, #f97316 0%, #ea580c 50%, #10b981 100%);
      border: 3px solid #38bdf8;
      box-shadow: 0 8px 25px rgba(249, 115, 22, 0.4), 0 0 20px rgba(16, 185, 129, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
      position: relative;
    }
    .kisan-avatar-btn:hover {
      transform: scale(1.08) translateY(-3px);
      box-shadow: 0 12px 32px rgba(249, 115, 22, 0.6), 0 0 28px rgba(16, 185, 129, 0.5);
    }
    .kisan-avatar-svg {
      width: 44px;
      height: 44px;
    }
    .kisan-pulse-ring {
      position: absolute;
      width: 100%;
      height: 100%;
      border-radius: 50%;
      border: 2px solid #10b981;
      animation: kisanPulse 2.4s infinite;
      pointer-events: none;
    }
    @keyframes kisanPulse {
      0% { transform: scale(1); opacity: 0.9; }
      70% { transform: scale(1.4); opacity: 0; }
      100% { transform: scale(1.4); opacity: 0; }
    }
    .kisan-online-dot {
      position: absolute;
      bottom: 2px;
      right: 2px;
      width: 14px;
      height: 14px;
      background: #10b981;
      border: 2px solid #0f172a;
      border-radius: 50%;
    }

    .kisan-bubble {
      position: absolute;
      right: 76px;
      bottom: 12px;
      background: rgba(15, 23, 42, 0.95);
      border: 1px solid rgba(56, 189, 248, 0.35);
      border-radius: 18px 18px 4px 18px;
      padding: 12px 18px;
      width: 260px;
      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5), 0 0 18px rgba(56, 189, 248, 0.15);
      font-size: 13px;
      color: #f8fafc;
      line-height: 1.45;
      opacity: 0;
      transform: translateX(12px) scale(0.95);
      pointer-events: none;
      transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .kisan-bubble.show {
      opacity: 1;
      transform: translateX(0) scale(1);
      pointer-events: auto;
    }
    .kisan-bubble-title {
      font-weight: 700;
      color: #38bdf8;
      font-size: 12px;
      margin-bottom: 3px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .kisan-chat-box {
      position: fixed;
      bottom: 100px;
      right: 26px;
      width: 400px;
      height: 580px;
      max-width: calc(100vw - 40px);
      max-height: calc(100vh - 120px);
      background: rgba(15, 23, 42, 0.94);
      border: 1px solid rgba(56, 189, 248, 0.3);
      border-radius: 22px;
      box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.8), 0 0 30px rgba(16, 185, 129, 0.2);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      z-index: 9999;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      opacity: 0;
      transform: translateY(20px) scale(0.95);
      pointer-events: none;
      transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .kisan-chat-box.open {
      opacity: 1;
      transform: translateY(0) scale(1);
      pointer-events: auto;
    }

    .kisan-chat-header {
      padding: 14px 18px;
      background: rgba(20, 35, 58, 0.85);
      border-bottom: 1px solid rgba(56, 189, 248, 0.18);
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .kisan-header-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .kisan-header-identity {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .kisan-avatar-sm {
      width: 38px;
      height: 38px;
      border-radius: 50%;
      background: linear-gradient(135deg, #f97316 0%, #10b981 100%);
      border: 2px solid #38bdf8;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .kisan-name {
      font-weight: 700;
      font-size: 15px;
      color: #f8fafc;
    }
    .kisan-status {
      font-size: 11.5px;
      color: #10b981;
      display: flex;
      align-items: center;
      gap: 5px;
    }
    .kisan-header-actions {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .kisan-icon-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 16px;
      padding: 4px;
      border-radius: 6px;
      transition: color 0.2s;
    }
    .kisan-icon-btn:hover {
      color: #f8fafc;
      background: rgba(255, 255, 255, 0.08);
    }

    .kisan-lang-bar {
      display: flex;
      align-items: center;
      background: rgba(10, 18, 30, 0.6);
      border-radius: 10px;
      padding: 3px;
      border: 1px solid rgba(56, 189, 248, 0.15);
      gap: 4px;
    }
    .kisan-lang-btn {
      flex: 1;
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-family: inherit;
      font-size: 12px;
      font-weight: 600;
      padding: 5px 0;
      border-radius: 7px;
      cursor: pointer;
      transition: all 0.2s ease;
      text-align: center;
    }
    .kisan-lang-btn.active {
      background: rgba(16, 185, 129, 0.25);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.5);
      font-weight: 700;
    }

    .kisan-messages {
      flex: 1;
      padding: 16px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 14px;
      scroll-behavior: smooth;
    }
    .kisan-msg-row {
      display: flex;
      gap: 9px;
      max-width: 88%;
      animation: msgPop 0.25s ease;
    }
    @keyframes msgPop {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .kisan-msg-row.bot { align-self: flex-start; }
    .kisan-msg-row.user { align-self: flex-end; flex-direction: row-reverse; }
    .kisan-msg-bubble {
      padding: 11px 15px;
      border-radius: 16px;
      font-size: 13.5px;
      line-height: 1.5;
      word-break: break-word;
    }
    .kisan-msg-row.bot .kisan-msg-bubble {
      background: rgba(30, 41, 59, 0.85);
      border: 1px solid rgba(56, 189, 248, 0.18);
      color: #f1f5f9;
      border-top-left-radius: 4px;
    }
    .kisan-msg-row.user .kisan-msg-bubble {
      background: linear-gradient(135deg, #059669 0%, #047857 100%);
      color: #ffffff;
      border-top-right-radius: 4px;
      box-shadow: 0 4px 14px rgba(5, 150, 105, 0.25);
    }
    .kisan-msg-time {
      font-size: 10px;
      color: var(--text-sub);
      margin-top: 4px;
      text-align: right;
    }

    .kisan-chips {
      padding: 6px 14px 10px 14px;
      display: flex;
      gap: 6px;
      overflow-x: auto;
      white-space: nowrap;
      scrollbar-width: none;
    }
    .kisan-chips::-webkit-scrollbar { display: none; }
    .kisan-chip {
      background: rgba(56, 189, 248, 0.1);
      border: 1px solid rgba(56, 189, 248, 0.25);
      color: #bae6fd;
      font-size: 11.5px;
      font-weight: 500;
      padding: 5px 11px;
      border-radius: 999px;
      cursor: pointer;
      transition: all 0.2s ease;
      flex-shrink: 0;
    }
    .kisan-chip:hover {
      background: rgba(16, 185, 129, 0.22);
      border-color: #10b981;
      color: #a7f3d0;
      transform: translateY(-1px);
    }

    .kisan-input-wrap {
      padding: 12px 14px;
      background: rgba(15, 23, 42, 0.95);
      border-top: 1px solid rgba(56, 189, 248, 0.15);
      display: flex;
      gap: 8px;
      align-items: center;
    }
    .kisan-input {
      flex: 1;
      background: rgba(10, 18, 30, 0.7);
      border: 1px solid rgba(56, 189, 248, 0.2);
      border-radius: 12px;
      padding: 10px 14px;
      color: #f8fafc;
      font-family: inherit;
      font-size: 13.5px;
      outline: none;
      transition: all 0.2s;
    }
    .kisan-input:focus {
      border-color: #10b981;
      box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.18);
    }
    .kisan-send-btn {
      width: 40px;
      height: 40px;
      border-radius: 12px;
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      color: white;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s;
      flex-shrink: 0;
    }
    .kisan-send-btn:hover {
      transform: scale(1.05);
      box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);
    }

    .kisan-settings-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(15, 23, 42, 0.96);
      z-index: 10;
      padding: 24px;
      display: none;
      flex-direction: column;
      animation: fadeInTab 0.2s ease;
    }
    .kisan-settings-overlay.show { display: flex; }
"""

# Insert CSS into </style>
content = content.replace("</style>", auth_and_chat_css + "\n  </style>")

# 2. Add User Badge in cloud-banner
user_badge_html = """
      <!-- Authenticated User Badge (§5.8) -->
      <div id="userBadgeWrap" style="display: flex; align-items: center; gap: 8px; margin-left: 8px;">
        <span style="color: #6ee7b7; font-size: 12px; font-weight: 600; background: rgba(16, 185, 129, 0.12); padding: 4px 10px; border-radius: var(--radius-sm); border: 1px solid rgba(16, 185, 129, 0.25);">
          👤 <span id="authUsername">Verified Farmer</span>
        </span>
        <button class="btn btn-outline" style="padding: 4px 9px; font-size: 11px; border-color: rgba(244, 63, 94, 0.35); color: #fda4af;" onclick="logoutUser()" title="Sign out of AgroNex">Sign Out</button>
      </div>
"""
target_pos = content.find('id="modePill"')
if target_pos != -1:
    content = content[:target_pos] + 'id="modePill_pre" ' + content[target_pos:]
    content = content.replace('id="modePill_pre" id="modePill"', user_badge_html + '      <span class="pill-badge pill-green" id="modePill"')

# 3. Add Verified Auth Modal Overlay right after <body>
farmer_svg_def = """<svg class="kisan-avatar-svg" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M22 38C20 22 36 10 50 10C64 10 80 22 78 38C76 44 70 48 64 50C54 53 46 53 36 50C30 48 24 44 22 38Z" fill="#F97316"/>
  <path d="M30 18C40 12 60 12 70 18C75 22 77 28 73 34C68 39 32 39 27 34C23 28 25 22 30 18Z" fill="#EA580C"/>
  <circle cx="50" cy="18" r="4.5" fill="#EAB308"/>
  <path d="M48 10L50 4L52 10Z" fill="#FACC15"/>
  <path d="M26 44C26 39 30 36 30 36H70C70 36 74 39 74 44C74 58 64 68 50 68C36 68 26 58 26 44Z" fill="#FED7AA"/>
  <circle cx="26" cy="46" r="4.5" fill="#FED7AA"/>
  <circle cx="74" cy="46" r="4.5" fill="#FED7AA"/>
  <circle cx="41" cy="45" r="2.5" fill="#1E293B"/>
  <circle cx="59" cy="45" r="2.5" fill="#1E293B"/>
  <circle cx="42" cy="44" r="0.8" fill="#FFFFFF"/>
  <circle cx="60" cy="44" r="0.8" fill="#FFFFFF"/>
  <path d="M35 56C42 54 48 56 50 58C52 56 58 54 65 56C67 57 66 59 62 58C56 56 52 61 50 61C48 61 44 56 38 58C34 59 33 57 35 56Z" fill="#1E293B"/>
  <path d="M44 62C47 64 53 64 56 62" stroke="#9A3412" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M24 74C22 84 20 96 20 100H80C80 96 78 84 76 74C68 70 58 68 50 68C42 68 32 70 24 74Z" fill="#F8FAFC"/>
  <path d="M36 70L28 100H40L46 70Z" fill="#10B981"/>
  <circle cx="42" cy="78" r="3" fill="#FACC15"/>
</svg>"""

auth_and_chat_html = f"""
  <!-- =========================================================================
       VERIFIED LOGIN & SIGN UP MODAL OVERLAY (§5.8)
       ========================================================================= -->
  <div id="authModalOverlay" class="auth-overlay">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-logo">🌱</div>
        <h2 class="auth-title">AgroNex-Pi Access Portal</h2>
        <p class="auth-subtitle">Autonomous Farm Maintenance & Robotics System</p>
      </div>

      <div class="auth-tabs">
        <button id="tabLoginBtn" class="auth-tab-btn active" onclick="switchAuthTab('login')">Verified Sign In</button>
        <button id="tabRegisterBtn" class="auth-tab-btn" onclick="switchAuthTab('register')">Farmer Register</button>
      </div>

      <!-- Login Form -->
      <form id="loginForm" onsubmit="handleLogin(event)">
        <div class="auth-form-group">
          <label class="auth-label">Username</label>
          <input type="text" id="loginUsername" class="auth-input" placeholder="e.g. admin or your username" required autocomplete="username">
        </div>
        <div class="auth-form-group">
          <label class="auth-label">Password</label>
          <input type="password" id="loginPassword" class="auth-input" placeholder="Enter your password" required autocomplete="current-password">
        </div>
        <button type="submit" id="loginSubmitBtn" class="auth-submit-btn">🔐 Sign In to Command Center</button>
      </form>

      <!-- Register Form -->
      <form id="registerForm" style="display:none;" onsubmit="handleRegister(event)">
        <div class="auth-form-group">
          <label class="auth-label">Full Name</label>
          <input type="text" id="regFullName" class="auth-input" placeholder="e.g. Ramesh Patil" required>
        </div>
        <div class="auth-form-group">
          <label class="auth-label">Desired Username</label>
          <input type="text" id="regUsername" class="auth-input" placeholder="e.g. farmer_ramesh" required autocomplete="username">
        </div>
        <div class="auth-form-group">
          <label class="auth-label">Password (Min 6 chars)</label>
          <input type="password" id="regPassword" class="auth-input" placeholder="Create strong password" required minlength="6" autocomplete="new-password">
        </div>
        <div class="auth-form-group">
          <label class="auth-label">Farmer Verification Key <span style="color:#f43f5e;">*</span></label>
          <input type="password" id="regVerifyKey" class="auth-input" placeholder="Enter farm secret key (e.g. AGRONEX_FARM_2026)" required>
          <small style="color:var(--text-sub);font-size:11px;margin-top:3px;display:block;">Required to ensure only authorized personnel access physical rover controls.</small>
        </div>
        <button type="submit" id="registerSubmitBtn" class="auth-submit-btn">✅ Verify & Create Account</button>
      </form>

      <div id="authStatusMsg" class="auth-msg"></div>

      <div class="auth-footer-hint">
        🛡️ Protected by AgroNex Secure Auth • Default Admin: <span style="color:#38bdf8;font-family:monospace;">admin / agronex2026</span>
      </div>
    </div>
  </div>

  <!-- Floating Action Button with Farmer Avatar -->
  <div class="kisan-fab" id="kisanFab" onclick="toggleKisanChat()">
    <div class="kisan-pulse-ring"></div>
    <div class="kisan-avatar-btn" title="Chat with AI Kisan Mitra (English, मराठी, हिन्दी)">
      {farmer_svg_def}
      <div class="kisan-online-dot"></div>
    </div>

    <!-- Entrance Greeting Bubble -->
    <div class="kisan-bubble" id="kisanBubble">
      <div class="kisan-bubble-title">
        <span>👨‍🌾 Kisan Mitra AI</span>
        <span style="font-size:10px;color:#10b981;">● Online</span>
      </div>
      <div id="bubbleText">Namaste! I am your AI Kisan Mitra. Click here for instant farm, disease, and rover advice!</div>
    </div>
  </div>

  <!-- Main Chat Drawer -->
  <div class="kisan-chat-box" id="kisanChatBox">
    <!-- Header -->
    <div class="kisan-chat-header">
      <div class="kisan-header-top">
        <div class="kisan-header-identity">
          <div class="kisan-avatar-sm">
            {farmer_svg_def}
          </div>
          <div>
            <div class="kisan-name" id="chatAssistantTitle">Kisan Mitra AI</div>
            <div class="kisan-status">● Live Rover Telemetry Linked</div>
          </div>
        </div>
        <div class="kisan-header-actions">
          <button class="kisan-icon-btn" onclick="openChatSettings()" title="Mistral AI API Key Settings">⚙️</button>
          <button class="kisan-icon-btn" onclick="clearChatHistory()" title="Clear Chat">🗑️</button>
          <button class="kisan-icon-btn" onclick="toggleKisanChat()" title="Close Chat">✕</button>
        </div>
      </div>

      <!-- Trilingual Language Switcher -->
      <div class="kisan-lang-bar">
        <button class="kisan-lang-btn active" id="langBtn_en" onclick="setChatLanguage('en')">English</button>
        <button class="kisan-lang-btn" id="langBtn_hi" onclick="setChatLanguage('hi')">हिन्दी</button>
        <button class="kisan-lang-btn" id="langBtn_mr" onclick="setChatLanguage('mr')">मराठी</button>
      </div>
    </div>

    <!-- Messages Container -->
    <div class="kisan-messages" id="kisanMessages"></div>

    <!-- Quick Prompt Chips -->
    <div class="kisan-chips" id="kisanChips"></div>

    <!-- Input Form -->
    <form class="kisan-input-wrap" onsubmit="handleSendChat(event)">
      <input type="text" id="kisanInput" class="kisan-input" placeholder="Ask about soil, crops, rover status, or diseases..." autocomplete="off">
      <button type="submit" id="kisanSendBtn" class="kisan-send-btn" title="Send Question">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
      </button>
    </form>

    <!-- Mistral API Key Modal Overlay inside Chat -->
    <div class="kisan-settings-overlay" id="kisanSettingsOverlay">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <h3 style="font-size:16px;font-weight:700;color:#f8fafc;">⚙️ Chatbot Intelligence Settings</h3>
        <button class="kisan-icon-btn" onclick="closeChatSettings()">✕</button>
      </div>
      <p style="font-size:12.5px;color:var(--text-muted);margin-bottom:16px;line-height:1.5;">
        Paste your <strong>Mistral AI API Key</strong> below to enable full LLM generative reasoning across English, Marathi, and Hindi. (You can also configure it in <code style="color:#38bdf8;">config.py</code>).
      </p>
      <div style="margin-bottom:16px;">
        <label style="display:block;font-size:12px;color:#cbd5e1;margin-bottom:6px;font-weight:600;">Mistral API Key</label>
        <input type="password" id="mistralApiKeyInput" class="auth-input" placeholder="Paste your api_key here...">
      </div>
      <div style="display:flex;gap:10px;margin-top:auto;">
        <button class="btn btn-emerald" style="flex:1;" onclick="saveMistralApiKey()">Save Key</button>
        <button class="btn btn-outline" onclick="closeChatSettings()">Cancel</button>
      </div>
    </div>
  </div>
"""

content = content.replace("<body>", "<body>\n" + auth_and_chat_html)

# 4. JavaScript Logic to inject before </script>
auth_and_chat_js = """
    /* =========================================================================
       VERIFIED AUTHENTICATION & LOGIN/SIGNUP JAVASCRIPT LOGIC (§5.8)
       ========================================================================= */
    let currentAuthUser = null;

    function getApiEndpoint(path) {
      if (typeof API_URL !== 'undefined' && API_URL && API_URL.startsWith('http')) {
        const base = API_URL.replace(/\\/$/, '');
        return base + (path.startsWith('/') ? path : '/' + path);
      }
      return path;
    }

    function switchAuthTab(tab) {
      const loginForm = document.getElementById('loginForm');
      const regForm = document.getElementById('registerForm');
      const tabLoginBtn = document.getElementById('tabLoginBtn');
      const tabRegBtn = document.getElementById('tabRegisterBtn');
      const statusMsg = document.getElementById('authStatusMsg');
      statusMsg.style.display = 'none';

      if (tab === 'login') {
        loginForm.style.display = 'block';
        regForm.style.display = 'none';
        tabLoginBtn.classList.add('active');
        tabRegBtn.classList.remove('active');
      } else {
        loginForm.style.display = 'none';
        regForm.style.display = 'block';
        tabLoginBtn.classList.remove('active');
        tabRegBtn.classList.add('active');
      }
    }

    async function handleLogin(e) {
      e.preventDefault();
      const u = document.getElementById('loginUsername').value.trim();
      const p = document.getElementById('loginPassword').value.trim();
      const msg = document.getElementById('authStatusMsg');
      const btn = document.getElementById('loginSubmitBtn');
      
      btn.disabled = true;
      btn.textContent = 'Verifying Credentials...';
      msg.className = 'auth-msg';
      msg.style.display = 'none';

      try {
        const resp = await fetch(getApiEndpoint('/api/auth/login'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: u, password: p })
        });
        const data = await resp.json();

        if (data.ok && data.token) {
          localStorage.setItem('agronex_auth_token', data.token);
          localStorage.setItem('agronex_auth_user', JSON.stringify(data.user));
          currentAuthUser = data.user;
          msg.className = 'auth-msg success';
          msg.textContent = '✓ Access Verified! Welcome, ' + data.user.full_name;
          msg.style.display = 'block';
          
          setTimeout(() => {
            unlockDashboard(data.user);
          }, 600);
        } else {
          msg.className = 'auth-msg error';
          msg.textContent = '✕ ' + (data.error || 'Invalid credentials');
          msg.style.display = 'block';
        }
      } catch (err) {
        msg.className = 'auth-msg error';
        msg.textContent = '✕ Connection error. Is rover web server online?';
        msg.style.display = 'block';
      } finally {
        btn.disabled = false;
        btn.textContent = '🔐 Sign In to Command Center';
      }
    }

    async function handleRegister(e) {
      e.preventDefault();
      const fn = document.getElementById('regFullName').value.trim();
      const u = document.getElementById('regUsername').value.trim();
      const p = document.getElementById('regPassword').value.trim();
      const key = document.getElementById('regVerifyKey').value.trim();
      const msg = document.getElementById('authStatusMsg');
      const btn = document.getElementById('registerSubmitBtn');

      btn.disabled = true;
      btn.textContent = 'Validating Verification Key...';
      msg.className = 'auth-msg';
      msg.style.display = 'none';

      try {
        const resp = await fetch(getApiEndpoint('/api/auth/register'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ full_name: fn, username: u, password: p, verification_key: key })
        });
        const data = await resp.json();

        if (data.ok) {
          msg.className = 'auth-msg success';
          msg.textContent = '✓ ' + data.message + ' Please sign in now.';
          msg.style.display = 'block';
          setTimeout(() => {
            switchAuthTab('login');
            document.getElementById('loginUsername').value = u;
            document.getElementById('loginPassword').value = '';
          }, 1200);
        } else {
          msg.className = 'auth-msg error';
          msg.textContent = '✕ ' + (data.error || 'Registration failed');
          msg.style.display = 'block';
        }
      } catch (err) {
        msg.className = 'auth-msg error';
        msg.textContent = '✕ Server connection error.';
        msg.style.display = 'block';
      } finally {
        btn.disabled = false;
        btn.textContent = '✅ Verify & Create Account';
      }
    }

    function unlockDashboard(user) {
      const overlay = document.getElementById('authModalOverlay');
      overlay.classList.add('hidden');
      const badgeWrap = document.getElementById('userBadgeWrap');
      if (badgeWrap) badgeWrap.style.display = 'flex';
      const uName = document.getElementById('authUsername');
      if (uName) uName.textContent = user.full_name || user.username;
    }

    function lockDashboard() {
      const overlay = document.getElementById('authModalOverlay');
      overlay.classList.remove('hidden');
      const badgeWrap = document.getElementById('userBadgeWrap');
      if (badgeWrap) badgeWrap.style.display = 'none';
    }

    async function checkAuthSession() {
      const token = localStorage.getItem('agronex_auth_token');
      const storedUser = localStorage.getItem('agronex_auth_user');

      if (!token || !storedUser) {
        lockDashboard();
        return;
      }

      try {
        const resp = await fetch(getApiEndpoint('/api/auth/status'), {
          headers: { 'Authorization': 'Bearer ' + token }
        });
        const data = await resp.json();
        if (data.authenticated) {
          currentAuthUser = data.user;
          unlockDashboard(data.user);
        } else {
          lockDashboard();
        }
      } catch (e) {
        if (storedUser) {
          try {
            currentAuthUser = JSON.parse(storedUser);
            unlockDashboard(currentAuthUser);
          } catch(err) { lockDashboard(); }
        } else {
          lockDashboard();
        }
      }
    }

    async function logoutUser() {
      const token = localStorage.getItem('agronex_auth_token');
      try {
        await fetch(getApiEndpoint('/api/auth/logout'), { method: 'POST' });
      } catch(e) {}
      localStorage.removeItem('agronex_auth_token');
      localStorage.removeItem('agronex_auth_user');
      currentAuthUser = null;
      lockDashboard();
    }


    /* =========================================================================
       KISAN MITRA TRILINGUAL AI CHATBOT (EN / MR / HI) JAVASCRIPT LOGIC
       ========================================================================= */
    let currentChatLang = 'en';
    let isChatOpen = false;
    let chatConversationHistory = [];

    const CHAT_LOCALES = {
      en: {
        title: "Kisan Mitra AI",
        greeting: "Namaste! I am your AI Kisan Mitra. How can I assist you with your farm and AgroNex-Pi rover today?",
        bubble: "Namaste! I am your AI Kisan Mitra. Click here for instant farm, disease, and rover advice!",
        placeholder: "Ask about soil, crops, rover status, or diseases...",
        chips: [
          "🌾 Check Soil & Pump Status",
          "🍅 Tomato Early Blight Cure",
          "🚜 Rover GPS & Safety State",
          "🌿 Tulsi Plant Care Guide"
        ]
      },
      mr: {
        title: "बळीराजा मित्र (ॲग्रोनेक्स)",
        greeting: "रामराम शेतकरी दादा! मी आपला 'बळीराजा मित्र' एआय सहाय्यक आहे. ॲग्रोनेक्स रोव्हर आणि पिकांच्या आरोग्याबद्दल काहीही विचारा!",
        bubble: "रामराम! मी आपला बळीराजा मित्र आहे. पिकांचे रोग किंवा रोव्हरबद्दल विचारण्यासाठी येथे क्लिक करा!",
        placeholder: "माती, पिके, रोव्हर स्थिती किंवा रोगांबद्दल विचारा...",
        chips: [
          "🌾 मातीतील ओलावा व पंपाची स्थिती",
          "🍅 टोमॅटोवरील करपा रोग उपाय",
          "🚜 रोव्हरची कार्यस्थिती व जीपीएस",
          "🌿 तुळशीच्या रोपाची काळजी"
        ]
      },
      hi: {
        title: "किसान मित्र (एग्रोनेक्स)",
        greeting: "नमस्ते किसान भाई! मैं आपका 'किसान मित्र' एआई सहायक हूँ। एग्रोनेक्स रोवर और फसलों के बारे में कोई भी प्रश्न पूछें!",
        bubble: "नमस्ते! मैं आपका किसान मित्र हूँ। फसलों के रोग या रोवर की जानकारी के लिए यहाँ क्लिक करें!",
        placeholder: "मिट्टी, फसल, रोवर या रोगों के बारे में पूछें...",
        chips: [
          "🌾 मिट्टी की नमी और पंप स्थिति",
          "🍅 टमाटर अगेती झुलसा का इलाज",
          "🚜 रोवर सुरक्षा और जीपीएस स्थिति",
          "🌿 तुलसी पौधे की देखभाल"
        ]
      }
    };

    function toggleKisanChat() {
      const box = document.getElementById('kisanChatBox');
      const bubble = document.getElementById('kisanBubble');
      isChatOpen = !isChatOpen;
      if (isChatOpen) {
        box.classList.add('open');
        bubble.classList.remove('show');
        document.getElementById('kisanInput').focus();
      } else {
        box.classList.remove('open');
      }
    }

    function setChatLanguage(lang) {
      if (!CHAT_LOCALES[lang]) return;
      currentChatLang = lang;

      ['en', 'mr', 'hi'].forEach(l => {
        const btn = document.getElementById(`langBtn_${l}`);
        if (btn) {
          if (l === lang) btn.classList.add('active');
          else btn.classList.remove('active');
        }
      });

      const loc = CHAT_LOCALES[lang];
      document.getElementById('chatAssistantTitle').textContent = loc.title;
      document.getElementById('bubbleText').textContent = loc.bubble;
      document.getElementById('kisanInput').placeholder = loc.placeholder;

      renderChatChips();

      if (chatConversationHistory.length === 0) {
        addBotMessage(loc.greeting);
      } else {
        addBotMessage(`✓ Switched to **${lang === 'mr' ? 'मराठी' : (lang === 'hi' ? 'हिन्दी' : 'English')}**.`);
      }
    }

    function renderChatChips() {
      const wrap = document.getElementById('kisanChips');
      const loc = CHAT_LOCALES[currentChatLang];
      wrap.innerHTML = loc.chips.map(chip => {
        return `<div class="kisan-chip" onclick="handleChipClick('${chip.replace(/'/g, "\\'")}')">${chip}</div>`;
      }).join('');
    }

    function handleChipClick(text) {
      const cleanText = text.replace(/^[\\u{1F300}-\\u{1F9FF}]\\s*/u, '');
      document.getElementById('kisanInput').value = cleanText;
      handleSendChat(new Event('submit'));
    }

    function formatChatMarkdown(txt) {
      if (!txt) return '';
      return txt
        .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
        .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.1);padding:2px 5px;border-radius:4px;font-size:12px;">$1</code>')
        .replace(/\\n/g, '<br>');
    }

    function addUserMessage(txt) {
      const msgs = document.getElementById('kisanMessages');
      const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const row = document.createElement('div');
      row.className = 'kisan-msg-row user';
      row.innerHTML = `
        <div class="kisan-msg-bubble">
          <div>${formatChatMarkdown(txt)}</div>
          <div class="kisan-msg-time">${timeStr}</div>
        </div>
      `;
      msgs.appendChild(row);
      msgs.scrollTop = msgs.scrollHeight;
    }

    function addBotMessage(txt) {
      const msgs = document.getElementById('kisanMessages');
      const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const row = document.createElement('div');
      row.className = 'kisan-msg-row bot';
      row.innerHTML = `
        <div class="kisan-msg-bubble">
          <div>${formatChatMarkdown(txt)}</div>
          <div class="kisan-msg-time">${timeStr}</div>
        </div>
      `;
      msgs.appendChild(row);
      msgs.scrollTop = msgs.scrollHeight;
    }

    function clearChatHistory() {
      chatConversationHistory = [];
      const msgs = document.getElementById('kisanMessages');
      msgs.innerHTML = '';
      addBotMessage(CHAT_LOCALES[currentChatLang].greeting);
    }

    async function handleSendChat(e) {
      if (e) e.preventDefault();
      const input = document.getElementById('kisanInput');
      const userText = input.value.trim();
      if (!userText) return;

      input.value = '';
      addUserMessage(userText);
      chatConversationHistory.push({ role: 'user', content: userText });

      const msgs = document.getElementById('kisanMessages');
      const typingRow = document.createElement('div');
      typingRow.className = 'kisan-msg-row bot';
      typingRow.id = 'typingIndicator';
      typingRow.innerHTML = `<div class="kisan-msg-bubble" style="color:var(--text-muted);font-style:italic;">🌾 Kisan Mitra is analyzing telemetry...</div>`;
      msgs.appendChild(typingRow);
      msgs.scrollTop = msgs.scrollHeight;

      const storedMistralKey = localStorage.getItem('agronex_mistral_key') || '';

      try {
        const resp = await fetch(getApiEndpoint('/api/chat'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: userText,
            language: currentChatLang,
            api_key: storedMistralKey,
            history: chatConversationHistory
          })
        });
        const data = await resp.json();
        const tEl = document.getElementById('typingIndicator');
        if (tEl) tEl.remove();

        if (data.ok && data.reply) {
          addBotMessage(data.reply);
          chatConversationHistory.push({ role: 'assistant', content: data.reply });
        } else {
          addBotMessage("Sorry, I could not process that request. Please try again.");
        }
      } catch (err) {
        const tEl = document.getElementById('typingIndicator');
        if (tEl) tEl.remove();
        addBotMessage("✕ Error communicating with the assistant. Check rover connection.");
      }
    }

    function openChatSettings() {
      const overlay = document.getElementById('kisanSettingsOverlay');
      const input = document.getElementById('mistralApiKeyInput');
      input.value = localStorage.getItem('agronex_mistral_key') || '';
      overlay.classList.add('show');
    }

    function closeChatSettings() {
      document.getElementById('kisanSettingsOverlay').classList.remove('show');
    }

    function saveMistralApiKey() {
      const val = document.getElementById('mistralApiKeyInput').value.trim();
      localStorage.setItem('agronex_mistral_key', val);
      closeChatSettings();
      addBotMessage("✓ **Mistral API Key Saved!** Advanced generative AI intelligence is now active.");
    }

    window.addEventListener('DOMContentLoaded', () => {
      checkAuthSession();
      renderChatChips();
      addBotMessage(CHAT_LOCALES[currentChatLang].greeting);

      setTimeout(() => {
        const b = document.getElementById('kisanBubble');
        if (b && !isChatOpen) {
          b.classList.add('show');
          setTimeout(() => {
            if (!isChatOpen) b.classList.remove('show');
          }, 7000);
        }
      }, 2200);
    });
"""

# Replace the last occurrence of </script> to avoid inserting into external script tag
last_script_close = content.rfind("</script>")
if last_script_close != -1:
    content = content[:last_script_close] + auth_and_chat_js + "\n  </script>" + content[last_script_close + 9:]

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Cleanly injected! Total lines in {html_path}: {len(content.splitlines())}")

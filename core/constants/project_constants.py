"""Constants và URLs cho Google Labs Video Generation API."""

# ========== BASE URLs ==========
GOOGLE_LABS_BASE_URL = "https://labs.google"
GOOGLE_SANDBOX_API_URL = "https://aisandbox-pa.googleapis.com/v1"

# ========== AUTH URLs ==========
AUTH_SESSION_URL = f"{GOOGLE_LABS_BASE_URL}/fx/api/auth/session"

# ========== PROJECT URLs ==========
CREATE_PROJECT_URL = f"{GOOGLE_LABS_BASE_URL}/fx/api/trpc/project.createProject"

# ========== IMAGE GENERATION URLs ==========
BATCH_GENERATE_IMAGES_URL = f"{GOOGLE_SANDBOX_API_URL}/projects/{{project_id}}/flowMedia:batchGenerateImages"

# ========== VIDEO GENERATION URLs ==========
BATCH_ASYNC_GENERATE_VIDEO_URL = f"{GOOGLE_SANDBOX_API_URL}/video:batchAsyncGenerateVideoStartImage"
CHECK_VIDEO_STATUS_URL = f"{GOOGLE_SANDBOX_API_URL}/video:batchCheckAsyncVideoGenerationStatus"
VIDEO_UPSAMPLE_URL = f"{GOOGLE_SANDBOX_API_URL}/video:batchAsyncGenerateVideoUpsampleVideo"

# ========== VIDEO CONCATENATION URLs ==========
CONCATENATE_VIDEOS_URL = f"{GOOGLE_LABS_BASE_URL}/fx/api/trpc/videoFx.runConcatenateVideos"
CHECK_CONCATENATION_STATUS_URL = f"{GOOGLE_SANDBOX_API_URL}:runVideoFxCheckConcatenationStatus"

# ========== GOOGLE SHEETS ==========
SPREADSHEET_ID = "1Fo8_W0IHsKpidGTtkrLIVoQ_AiZxn7U0VYG-LXGF2VM"
SHEET_RANGE = "Trang tính1!A1:D1"

# ========== MODEL KEYS ==========
MODEL_VIDEO_KEYS = {
    "veo3": "veo_3_1_i2v_s_fast_ultra_relaxed"
    }
MODEL_IMAGE_KEYS = {
    "nano_banana_pro": "GEM_PIX_2"
    }

# ========== GEMINI KEYS ==========
GEMENI_KEY = "AIzaSyDIBGGiaetBzYR0cB7DsshgLZa5su_wmq4"
# ========== IMAGE SETTINGS ==========
IMAGE_ASPECT_RATIO = "IMAGE_ASPECT_RATIO_LANDSCAPE"
VIDEO_ASPECT_RATIO = "VIDEO_ASPECT_RATIO_LANDSCAPE"

# ========== TIMEOUTS & DELAYS ==========
API_TIMEOUT = 30  # seconds
POLL_INTERVAL = 10  # seconds
MAX_RETRIES = 120  # Số lần retry tối đa khi check status
SCENES_PER_BATCH = 4  # Số scenes gen cùng lúc trong mỗi batch

# ========== STATUS CODES ==========
STATUS_SUCCESSFUL = "MEDIA_GENERATION_STATUS_SUCCESSFUL"
STATUS_FAILED = "MEDIA_GENERATION_STATUS_FAILED"
STATUS_ACTIVE = "MEDIA_GENERATION_STATUS_ACTIVE"

# ========== TOOL & CLIENT CONTEXT ==========
TOOL_NAME = "PINHOLE"
USER_PAYGATE_TIER = "PAYGATE_TIER_TWO"

# ========== GOOGLE ANALYTICS ==========
GA_DEFAULT = "GA1.1.2146137553.1763265710"
GA_CODE = "_ga_X2GNH8R5NS"
GA_X2GNH8R5NS_VALUE = "GS2.1.s1763468923$o3$g1$t1763468958$j25$l0$h658479695"
GA_SECONDARY = "GA1.1.1251170627.1758080857"
GA_X5V89YHGSH = "GS2.1.s1759372343$o3$g1$t1759374185$j51$l0$h0"
GA_5K7X2T4V16 = "GS2.1.s1759372345$o2$g1$t1759373912$j57$l0$h0"
GA_4L3D49E8S8 = "GS2.1.s1759598989$o2$g0$t1759598995$j54$l0$h0"
GA_X2GNH8R5NS_SECONDARY = "GS2.1.s1761200656^$o3^$g1^$t1761203925^$j60^$l0^$h2053918754"
GA_X5V89YHGSH_SECONDARY = "GS2.1.s1761203567^$o1^$g1^$t1761203637^$j60^$l0^$h0"

# ========== COOKIE VALUES ==========
CALLBACK_URL_ENCODED = "https%3A%2F%2Flabs.google%2Ffx"
CALLBACK_URL_WITH_PROJECT = "https%3A%2F%2Flabs.google%2Ffx%2Fvi%2Ftools%2Fflow%2Fproject%2F36695f4e-8ae8-4acd-96d0-9a9acea22856"

# ========== USER AGENT ==========
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

"""Generate script UI for AITool"""
import tkinter as tk
from tkinter import scrolledtext, simpledialog
import tkinter.font as tkfont
import json
import threading
import time
from PIL import Image, ImageTk
from io import BytesIO
import requests
import base64
import re
from core.service import generate_script_service
from core.service import generate_character_service
from core.subflowgenvideo.create_image import create_image
# Note: using create_image subflow directly. The function may return either a string media_id or a dict with image_uri.
from core.view import notification
from core.constants import project_constants
from core.constants import animation_styles

# Import mainflow helpers to auto-create project without prompting
from core.mainflowgenVideo.get_config_sheet import get_token_from_sheet
from core.mainflowgenVideo.email_parse import email_parse
from core.mainflowgenVideo.token_setup import build_token_setup
from core.mainflowgenVideo.create_project import create_project

# UI Colors
BG = "#181818"
PANEL = "#1f1f1f"
TEXT = "#e6e6e6"
SUB = "#9aa0a6"
ACCENT = "#00a67e"


def create_generate_frame(parent, show_home_callback):
    """Create generate script page frame"""
    frame = tk.Frame(parent, bg=BG)
    
    # Fonts
    header_font = tkfont.Font(family="Segoe UI", size=20, weight="bold")
    sub_font = tkfont.Font(family="Segoe UI", size=12)
    mono_font = tkfont.Font(family="Courier New", size=10)

    container = tk.Frame(frame, bg=BG, padx=20, pady=20)
    container.pack(fill=tk.BOTH, expand=True)

    top = tk.Frame(container, bg=BG)
    top.pack(fill=tk.X)

    title = tk.Label(top, text="Gen Kịch Bản", bg=BG, fg=TEXT, font=header_font)
    title.pack(anchor='w')
    subtitle = tk.Label(top, text="Tạo kịch bản phim hoạt hình cổ tích", bg=BG, fg=SUB, font=sub_font)
    subtitle.pack(anchor='w', pady=(4, 12))

    # Make split frame for left (controls + gallery) and right (JSON) panels
    split_frame = tk.Frame(container, bg=BG)
    split_frame.pack(fill=tk.BOTH, expand=True)

    left_frame = tk.Frame(split_frame, bg=BG)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

    right_frame = tk.Frame(split_frame, bg=BG)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Control Panel (left side)
    control_panel = tk.Frame(left_frame, bg=PANEL, padx=16, pady=12)
    control_panel.pack(fill=tk.X, pady=(0, 12))

    # Row 1: Số scene
    row1 = tk.Frame(control_panel, bg=PANEL)
    row1.pack(fill=tk.X, pady=(0, 10))

    lbl_scenes = tk.Label(row1, text="Số Scene:", bg=PANEL, fg=TEXT, font=("Segoe UI", 11))
    lbl_scenes.pack(side=tk.LEFT, padx=(0, 8))

    scenes_var = tk.StringVar(value=str(project_constants.DEFAULT_NUM_SCENES))
    spin_scenes = tk.Spinbox(row1, from_=1, to=50, textvariable=scenes_var, width=8, bg="#2b2b2b", fg=TEXT, insertbackground=TEXT, font=("Segoe UI", 11))
    spin_scenes.pack(side=tk.LEFT)

    # Row 2: Số nhân vật
    row2 = tk.Frame(control_panel, bg=PANEL)
    row2.pack(fill=tk.X, pady=(0, 10))

    lbl_chars = tk.Label(row2, text="Số Nhân Vật:", bg=PANEL, fg=TEXT, font=("Segoe UI", 11))
    lbl_chars.pack(side=tk.LEFT, padx=(0, 8))

    chars_var = tk.StringVar(value=str(project_constants.DEFAULT_NUM_CHARACTERS))
    spin_chars = tk.Spinbox(row2, from_=1, to=20, textvariable=chars_var, width=8, bg="#2b2b2b", fg=TEXT, insertbackground=TEXT, font=("Segoe UI", 11))
    spin_chars.pack(side=tk.LEFT)

    # Row 3: Animation style
    row3 = tk.Frame(control_panel, bg=PANEL)
    row3.pack(fill=tk.X, pady=(0, 10))

    lbl_style = tk.Label(row3, text="Phong Cách:", bg=PANEL, fg=TEXT, font=("Segoe UI", 11))
    lbl_style.pack(side=tk.LEFT, padx=(0, 8))

    style_var = tk.StringVar(value="3d")
    style_options = animation_styles.get_style_names()
    style_combo = tk.OptionMenu(row3, style_var, *style_options.keys())
    style_combo.config(bg="#2b2b2b", fg=TEXT, highlightthickness=0)
    style_combo["menu"].config(bg="#2b2b2b", fg=TEXT, activebackground=ACCENT, activeforeground=BG)
    style_combo.pack(side=tk.LEFT)

    # Status label
    status_label = tk.Label(control_panel, text="", bg=PANEL, fg=SUB, font=("Segoe UI", 10))
    status_label.pack(fill=tk.X, pady=(0, 8))

    # Informational label: using hardcoded access token
    info_label = tk.Label(control_panel, text="Access token: (hardcoded)", bg=PANEL, fg=SUB, font=("Segoe UI", 9))
    info_label.pack(fill=tk.X, padx=(4,0))

    # Character image section (left side)
    char_section_title = tk.Label(left_frame, text="Hình Nhân Vật", bg=BG, fg=TEXT, font=("Segoe UI", 12, "bold"))
    char_section_title.pack(anchor='w', pady=(12, 8))

    # Canvas for horizontal scrolling of character cards
    char_canvas_frame = tk.Frame(left_frame, bg=PANEL, height=580)
    char_canvas_frame.pack(fill=tk.X, pady=(0, 12))
    char_canvas_frame.pack_propagate(False)

    char_canvas = tk.Canvas(char_canvas_frame, bg="#1a1a1a", highlightthickness=0, height=580)
    char_scrollbar = tk.Scrollbar(char_canvas_frame, orient=tk.HORIZONTAL, command=char_canvas.xview)
    
    char_canvas.config(xscrollcommand=char_scrollbar.set)
    char_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    char_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    char_frame = tk.Frame(char_canvas, bg="#1a1a1a")
    char_canvas.create_window((0, 0), window=char_frame, anchor='nw')

    # Button area (left side, above gallery)
    btn_frame = tk.Frame(left_frame, bg=BG)
    btn_frame.pack(fill=tk.X, pady=(12, 12))

    gen_btn = tk.Button(
        btn_frame, text="Tạo Kịch Bản", command=None,  # Will be set later
        bg=ACCENT, fg=BG, bd=0, relief='flat', font=("Segoe UI", 10, "bold")
    )
    gen_btn.pack(side=tk.RIGHT, padx=(0, 8))

    # Retry button (for quota errors) - disabled by default
    retry_btn = tk.Button(
        btn_frame, text="Thử lại", command=None,
        bg="#ff9800", fg=BG, bd=0, relief='flat', font=("Segoe UI", 10, "bold")
    )
    retry_btn.pack(side=tk.RIGHT, padx=(0, 8))
    retry_btn.config(state=tk.DISABLED)

    back_btn = tk.Button(
        btn_frame, text="Quay lại", command=show_home_callback,
        bg="#444444", fg=TEXT, bd=0, relief='flat', font=("Segoe UI", 10)
    )
    back_btn.pack(side=tk.RIGHT)

    # Image generation progress label
    image_progress_label = tk.Label(left_frame, text="", bg=BG, fg=SUB, font=("Segoe UI", 10))
    image_progress_label.pack(anchor='w', pady=(0, 6))

    # Output display (right side)
    display_frame = tk.Frame(right_frame, bg=PANEL)
    display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))  # Fill right panel

    output_text = scrolledtext.ScrolledText(
        display_frame,
        bg="#1a1a1a",
        fg=TEXT,
        font=mono_font,
        padx=12,
        pady=12,
        wrap=tk.WORD,
        height=3  # Show only 3 lines
    )
    output_text.pack(fill=tk.BOTH, expand=True)
    output_text.config(state=tk.DISABLED)

    # Store script data
    script_data = {"script": None, "characters_with_images": []}

    def create_character_card(parent, char_data, char_index):
        # Ensure non-null char_data
        if char_data is None:
            char_data = {}
        """Create a character card widget"""
        card = tk.Frame(parent, bg=PANEL, padx=12, pady=12, width=360, height=550)
        card.pack(side=tk.LEFT, padx=6, fill=tk.Y)
        card.pack_propagate(False)

        # Character name
        # Show a fallback label for empty/blank names
        name_text = (char_data.get("name") or "").strip() or "Unknown"
        name_label = tk.Label(card, text=name_text, bg=PANEL, fg=TEXT, font=("Segoe UI", 10, "bold"), wraplength=200)
        name_label.pack(pady=(0, 8))

        # Status label for image generation
        status_label_card = tk.Label(card, text="Chưa gen", bg=PANEL, fg=SUB, font=("Segoe UI", 9))
        status_label_card.pack(pady=(0, 4))

        # Create a fixed-size frame container for the image
        image_container = tk.Frame(card, bg="#0a0a0a", width=336, height=189)
        image_container.pack(pady=(0, 8))
        image_container.pack_propagate(False)
        
        # Image label inside the container
        image_label = tk.Label(image_container, text="[Đang tải...]", bg="#0a0a0a", fg=SUB, font=("Segoe UI", 9))
        image_label.pack(fill=tk.BOTH, expand=True)

        # Prompt text area (scrollable, multi-line)
        prompt_text = (char_data.get("image_prompt") or char_data.get("description") or "").strip()
        prompt_textbox = scrolledtext.ScrolledText(
            card, 
            width=40, 
            height=4,
            bg="#2b2b2b", 
            fg=TEXT, 
            insertbackground=TEXT, 
            font=("Segoe UI", 9),
            wrap=tk.WORD,
            padx=4,
            pady=4
        )
        prompt_textbox.insert("1.0", prompt_text)
        prompt_textbox.pack(pady=(0, 8), fill=tk.X)

        # Regenerate button
        regen_btn = tk.Button(
            card, text="Gen Lại", bg=ACCENT, fg=BG, bd=0, relief='flat',
            font=("Segoe UI", 9, "bold"), padx=8, pady=4
        )
        regen_btn.pack(fill=tk.X)

        # Debug button to print card data into log
        debug_btn = tk.Button(card, text="Debug", bg="#333333", fg=TEXT, bd=0, relief='flat', font=("Segoe UI", 8), padx=4, pady=2)
        debug_btn.pack(fill=tk.X, pady=(4, 0))
        # Wire debug to print card data in right-hand output_text
        def _debug_card():
            try:
                output_text.config(state=tk.NORMAL)
                output_text.insert(tk.END, f"\n-- Debug Card {char_index} --\n")
                output_text.insert(tk.END, json.dumps(char_data, ensure_ascii=False, indent=2))
                output_text.insert(tk.END, f"\n-- End Card {char_index} --\n")
                output_text.config(state=tk.DISABLED)
            except Exception:
                pass

        debug_btn.config(command=_debug_card)

        return {
            "card": card,
            "name_label": name_label,
            "image_label": image_label,
            "prompt_textbox": prompt_textbox,
            "regen_btn": regen_btn,
            "status_label": status_label_card,
            "debug_btn": debug_btn,
            "char_data": char_data
        }

    def populate_character_cards(characters):
        """Populate character cards in the canvas"""
        # Clear existing cards
        for widget in char_frame.winfo_children():
            widget.destroy()

        script_data["characters_with_images"] = []

        if not characters:
            # Show a friendly message when there are no characters
            empty_lbl = tk.Label(char_frame, text="Không có nhân vật để hiển thị", bg="#1a1a1a", fg=SUB, font=("Segoe UI", 11))
            empty_lbl.pack(pady=20, padx=20)
            char_frame.update_idletasks()
            char_canvas.config(scrollregion=char_canvas.bbox("all"))
            return

        try:
            output_text.config(state=tk.NORMAL)
            output_text.insert(tk.END, f"\n[v0] Creating {len(characters)} character cards...\n")
            output_text.config(state=tk.DISABLED)
        except Exception:
            pass

        for i, char in enumerate(characters):
            card_data = create_character_card(char_frame, char, i)
            script_data["characters_with_images"].append(card_data)
            
            try:
                output_text.config(state=tk.NORMAL)
                output_text.insert(tk.END, f"[v0] Card {i} created: {char.get('name', 'Unknown')}\n")
                output_text.config(state=tk.DISABLED)
            except Exception:
                pass

        char_frame.update_idletasks()
        char_canvas.config(scrollregion=char_canvas.bbox("all"))
        char_canvas_frame.update()
        
        try:
            bbox = char_canvas.bbox("all")
            output_text.config(state=tk.NORMAL)
            output_text.insert(tk.END, f"[v0] Canvas bbox after populate: {bbox}\n")
            output_text.insert(tk.END, f"[v0] Char_frame children count: {len(char_frame.winfo_children())}\n")
            output_text.config(state=tk.DISABLED)
        except Exception:
            pass
        
        # Wire regenerate buttons after cards are created
        for idx, card in enumerate(script_data["characters_with_images"]):
            card["regen_btn"].config(command=make_regen_handler(idx))

    # Session storage for token/project
    # Default: use hardcoded access token to avoid modal prompting (change this if you need a different token)
    _session = {"access_token": "ya29.a0Aa7pCA_X6Zznis7yz80-bY7mcDhnZ_Gk6gwzd94bbgEbNpJTgWLDxe-cuJP3ZtseSNlWr7eUHocGHEWObd4P4Ck0GVDIG3hOodeYzxGyAiWL55zV0d4rRdIGLUAL5l4eRJwzg2bDU6mg9AyGK9hFpWjpmF16cNwjgYPG5hVqVpSKyaH4r87MOAacOrTDoiAvDoBqXeFyTume6400WFnLECqNSc8cHpncmizQqYWlD2Xd1sZ32UnFw37kwOknQ6FWu6RMQJEzSe-bdDCpvbKBe4TSFN99nFJx2hDlJWVg84Rduhh6n92hTtyNPjhtnzXguBWsFjBtjP3F_Bnu6hQvVtd1fr885L80HUC0TlyPWjYaCgYKAVQSARISFQHGX2Mi3DOex1QH-0BEZg_YpF4hxg0370", "project_id": None}

    def ensure_project_id():
        """Automatically create project if not present in session.
        Uses mainflow helpers to build cookies and create a new project.
        """
        if _session.get('project_id'):
            return _session['project_id']

        try:
            output_text.config(state=tk.NORMAL)
            output_text.insert(tk.END, "\nRetrieving token from sheet...\n")
            output_text.config(state=tk.DISABLED)
            token_data = get_token_from_sheet(output_text)
            if not token_data:
                notification.show_notification(frame, "✗ Không lấy được token từ sheet", type_="failed")
                return None

            email_data = email_parse(token_data.get('email', ''))
            token_setup = build_token_setup(token_data, email_data)
            cookie_string = token_setup.get('cookie')
            if not cookie_string:
                notification.show_notification(frame, "✗ Không tạo được cookie từ token setup", type_="failed")
                return None

            proj = create_project(cookie_string, output_text)
            if proj:
                _session['project_id'] = proj
                status_label.config(text=f"✅ Project sẵn sàng: {proj}")
                try:
                    output_text.config(state=tk.NORMAL)
                    output_text.insert(tk.END, f"\nCreated project: {proj}\n")
                    output_text.config(state=tk.DISABLED)
                except Exception:
                    pass
                return proj
            else:
                notification.show_notification(frame, "✗ Không tạo được project", type_="failed")
                return None
        except Exception as e:
            notification.show_notification(frame, f"✗ Lỗi tạo project: {str(e)}", type_="failed")
            return None

    def get_access_info():
        # Access token is pre-set; auto-create / reuse project id using mainflow
        if not _session.get('project_id'):
            pid = ensure_project_id()
            _session['project_id'] = pid
        return _session['access_token'], _session['project_id']

    def find_media_uri(obj):
        if isinstance(obj, dict):
            # If any value is an HTTP(S) URL string, return it
            for k, v in obj.items():
                if isinstance(v, str) and (v.startswith('http://') or v.startswith('https://')):
                    return v
            # Keep existing explicit key checks for backward compatibility
            if 'uri' in obj and isinstance(obj['uri'], str) and obj['uri'].startswith('http'):
                return obj['uri']
            if 'downloadUri' in obj and isinstance(obj['downloadUri'], str) and obj['downloadUri'].startswith('http'):
                return obj['downloadUri']
            if 'media' in obj and isinstance(obj['media'], list):
                for m in obj['media']:
                    uri = find_media_uri(m)
                    if uri:
                        return uri
            for v in obj.values():
                uri = find_media_uri(v)
                if uri:
                    return uri
        elif isinstance(obj, list):
            for item in obj:
                uri = find_media_uri(item)
                if uri:
                    return uri
            # If list contains a plain URL string, return it
            for item in obj:
                if isinstance(item, str) and (item.startswith('http://') or item.startswith('https://')):
                    return item
        return None

    def find_base64_image(obj):
        """Recursively search obj for base64 image data and return bytes if found."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                b = find_base64_image(v)
                if b:
                    return b
        elif isinstance(obj, list):
            for item in obj:
                b = find_base64_image(item)
                if b:
                    return b
        elif isinstance(obj, str):
            s = obj.strip()
            # Data URI like data:image/png;base64,AAAA...
            if s.startswith('data:image/') and 'base64,' in s:
                try:
                    payload = s.split('base64,', 1)[1]
                    return base64.b64decode(payload)
                except Exception:
                    return None
            # Raw base64 string heuristics: fairly long and only base64 chars
            if len(s) > 100 and re.match(r'^[A-Za-z0-9+/=\n\r]+$', s):
                try:
                    # remove whitespace/newlines
                    payload = re.sub(r'\s+', '', s)
                    return base64.b64decode(payload)
                except Exception:
                    return None
        return None

    def load_and_display_image(url, label):
        """Fetches an image from a URL and displays it in a tkinter Label."""
        try:
            output_text.config(state=tk.NORMAL)
            output_text.insert(tk.END, f"[v0] Fetching image URL:\n{url}\n")
            output_text.config(state=tk.DISABLED)
            
            headers = {"User-Agent": "Mozilla/5.0", "Accept": "image/*,*/*;q=0.8"}
            response = requests.get(url, timeout=15, headers=headers, allow_redirects=True)
            
            output_text.config(state=tk.NORMAL)
            output_text.insert(tk.END, f"[v0] Image response: status={response.status_code}, type={response.headers.get('content-type')}\n")
            output_text.config(state=tk.DISABLED)
            
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                pil_image = Image.open(image_data)
                
                pil_image.thumbnail((336, 189), Image.Resampling.LANCZOS)
                
                tk_image = ImageTk.PhotoImage(pil_image)
                label.config(image=tk_image, text="")
                label.image = tk_image
                
                output_text.config(state=tk.NORMAL)
                output_text.insert(tk.END, f"[v0] Image displayed successfully in label\n")
                output_text.config(state=tk.DISABLED)
                
                char_frame.update_idletasks()
                char_canvas.config(scrollregion=char_canvas.bbox("all"))
                char_canvas_frame.update()
            else:
                # Not an image or error status
                try:
                    output_text.config(state=tk.NORMAL)
                    output_text.insert(tk.END, f"\n[v0] Image fetch failed: status={response.status_code}, content-type={response.headers.get('content-type')}\n")
                    output_text.config(state=tk.DISABLED)
                except Exception:
                    pass
                label.config(text=f"[Không tải được]\nHTTP {response.status_code}\n{response.headers.get('content-type')}")
        except Exception as e:
            try:
                output_text.config(state=tk.NORMAL)
                output_text.insert(tk.END, f"\n[v0] Image fetch exception: {str(e)}\n")
                output_text.config(state=tk.DISABLED)
            except Exception:
                pass
            label.config(text=f"[Lỗi tải ảnh]\n{str(e)[:20]}")

    def display_image_from_bytes(img_bytes, label):
        """Displays image from bytes in a label."""
        try:
            image_data = BytesIO(img_bytes)
            pil_image = Image.open(image_data)
            
            pil_image.thumbnail((336, 189), Image.Resampling.LANCZOS)
            
            tk_image = ImageTk.PhotoImage(pil_image)
            label.config(image=tk_image, text="")
            label.image = tk_image
            
            char_frame.update_idletasks()
            char_canvas.config(scrollregion=char_canvas.bbox("all"))
            char_canvas_frame.update()
        except Exception as e:
            label.config(text=f"[Lỗi inline]\n{str(e)[:20]}")

    def make_regen_handler(index: int):
        def handler():
            output_text.config(state=tk.NORMAL)
            output_text.insert(tk.END, f"\n[v0] Regenerating character {index}...\n")
            output_text.config(state=tk.DISABLED)
            
            if index >= len(script_data.get("characters_with_images", [])):
                notification.show_notification(frame, "✗ Không tìm thấy nhân vật", type_="failed")
                return

            card = script_data["characters_with_images"][index]
            char = card["char_data"]
            image_label = card["image_label"]
            user_prompt = card["prompt_textbox"].get("1.0", tk.END).strip() # Get text from ScrolledText

            if not user_prompt:
                notification.show_notification(frame, "✗ Prompt không được để trống", type_="failed")
                return

            if card.get("status_label"):
                card["status_label"].config(text="Đang gen...", fg=ACCENT)
            image_label.config(text="[Đang tải...]", fg=SUB)
            image_label.image = None
            
            frame.update_idletasks()

            def _regen():
                try:
                    full_prompt = user_prompt if user_prompt != char.get("image_prompt") else char.get("image_prompt")
                    
                    # Call the official create_image subflow directly
                    create_result = create_image(project_id, access_token, index, full_prompt, log=output_text)

                    # Normalize result
                    if isinstance(create_result, dict):
                        image_url = create_result.get('image_uri') or create_result.get('uri') or None
                        # Also inspect raw_response for any URL fields
                        if not image_url and create_result.get('raw_response'):
                            try:
                                rr = create_result.get('raw_response')
                                candidate = find_media_uri(rr)
                                if candidate:
                                    image_url = candidate
                                    try:
                                        output_text.config(state=tk.NORMAL)
                                        output_text.insert(tk.END, f"\nFound URL in raw_response: {candidate}\n")
                                        output_text.config(state=tk.DISABLED)
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                        media_id = create_result.get('media_id') or create_result.get('mediaId')
                    else:
                        image_url = None
                        media_id = create_result

                    if image_url:
                        def update_gui():
                            load_and_display_image(image_url, image_label)
                            if card.get("status_label"):
                                card["status_label"].config(text="Đã gen", fg=ACCENT)
                            notification.show_notification(frame, f"✓ {char.get('name')} đã gen xong", type_="success")
                        
                        frame.after(0, update_gui)
                        return

                    # Check for inline/base64 image data in create_result
                    if isinstance(create_result, dict):
                        b = find_base64_image(create_result)
                        if b:
                            def update_gui_inline():
                                display_image_from_bytes(b, image_label)
                                if card.get("status_label"):
                                    card["status_label"].config(text="Đã gen", fg=ACCENT)
                                notification.show_notification(frame, f"✓ {char.get('name')} đã gen xong (inline)", type_="success")
                            
                            frame.after(0, update_gui_inline)
                            return

                    if media_id:
                        # Try a few common endpoints to fetch metadata containing a downloadUri or uri
                        candidates = [
                            f"{project_constants.GOOGLE_SANDBOX_API_URL}/projects/{project_id}/media/{media_id}",
                            f"{project_constants.GOOGLE_SANDBOX_API_URL}/projects/{project_id}/media/{media_id}:get",
                            f"{project_constants.GOOGLE_SANDBOX_API_URL}/projects/{project_id}/flowMedia/{media_id}",
                            f"{project_constants.GOOGLE_SANDBOX_API_URL}/media/{media_id}",
                        ]
                        headers = {"Authorization": f"Bearer {access_token}", "content-type": "application/json"}

                        found = False
                        for candidate in candidates:
                            try:
                                rr = requests.get(candidate, headers=headers, timeout=10)
                                try:
                                    output_text.config(state=tk.NORMAL)
                                    output_text.insert(tk.END, f"\nChecking candidate: {candidate} -> {rr.status_code}\n")
                                    output_text.config(state=tk.DISABLED)
                                except Exception:
                                    pass
                                if rr.status_code == 200:
                                    dd = rr.json()
                                    uri = find_media_uri(dd)
                                    if uri:
                                        def update_gui():
                                            load_and_display_image(uri, image_label)
                                            if card.get("status_label"):
                                                card["status_label"].config(text="Đã gen", fg=ACCENT)
                                            notification.show_notification(frame, f"✓ {char.get('name')} đã gen xong", type_="success")
                                        
                                        frame.after(0, update_gui)
                                        found = True
                                        break
                                    # Check for inline/base64 in metadata
                                    b2 = find_base64_image(dd)
                                    if b2:
                                        def update_gui_b64():
                                            display_image_from_bytes(b2, image_label)
                                            if card.get("status_label"):
                                                card["status_label"].config(text="Đã gen", fg=ACCENT)
                                            notification.show_notification(frame, f"✓ {char.get('name')} đã gen xong (inline)", type_="success")
                                        
                                        frame.after(0, update_gui_b64)
                                        found = True
                                        break
                            except Exception:
                                pass

                        if found:
                            return

                        def update_gui_media_id():
                            image_label.config(text=f"[Đã gen: {media_id}]", fg=SUB)
                            if card.get("status_label"):
                                card["status_label"].config(text=f"Đã gen (ID)", fg=ACCENT)
                            notification.show_notification(frame, f"✓ {char.get('name')} đã gen (media_id)", type_="success")
                        
                        frame.after(0, update_gui_media_id)
                        return

                    def update_gui_error():
                        image_label.config(text="[Không có uri]", fg="#ef4444")
                        if card.get("status_label"):
                            card["status_label"].config(text="Lỗi gen", fg="#ef4444")
                        notification.show_notification(frame, f"✗ Không lấy được ảnh {char.get('name')}", type_="failed")
                    
                    frame.after(0, update_gui_error)
                    
                except Exception as e:
                    def update_gui_exception():
                        image_label.config(text=f"[Lỗi gen]\n{str(e)[:30]}")
                        if card.get("status_label"):
                            card["status_label"].config(text="Lỗi gen", fg="#ef4444")
                        notification.show_notification(frame, f"✗ Lỗi: {str(e)}", type_="failed")
                    
                    frame.after(0, update_gui_exception)

            threading.Thread(target=_regen, daemon=True).start()

        return handler

    def generate_all_images():
        access_token, project_id = get_access_info()
        if not access_token:
            notification.show_notification(frame, "✗ Cần access token", type_="failed")
            return
        if not project_id:
            notification.show_notification(frame, "✗ Không thể tạo project - kiểm tra logs", type_="failed")
            return

        def _gen_all():
            total = len(script_data.get("characters_with_images", []))
            if total == 0:
                try:
                    frame.after(0, lambda: image_progress_label.config(text="Không có nhân vật để gen"))
                except Exception:
                    pass
                return
            try:
                frame.after(0, lambda: image_progress_label.config(text=f"Gen ảnh: 0/{total}"))
            except Exception:
                pass

            completed_count = [0]  # Use list to avoid closure issues
            lock = threading.Lock()

            def increment_completed():
                with lock:
                    completed_count[0] += 1
                    count = completed_count[0]
                try:
                    frame.after(0, lambda: image_progress_label.config(text=f"Gen ảnh: {count}/{total}"))
                except Exception:
                    pass
                
                if count >= total:
                    try:
                        frame.after(0, lambda: image_progress_label.config(text=f"Hoàn thành: {total}/{total}"))
                    except Exception:
                        pass

            for i in range(total):
                card = script_data["characters_with_images"][i]
                char = card["char_data"]
                image_label = card["image_label"]
                user_prompt = card["prompt_textbox"].get("1.0", tk.END).strip() # Get text from ScrolledText

                if not user_prompt:
                    increment_completed()
                    continue

                try:
                    frame.after(0, lambda c=card: c.get("status_label") and c["status_label"].config(text="Đang gen...", fg=ACCENT))
                    frame.after(0, lambda lbl=image_label: lbl.config(text="[Đang tải...]", fg=SUB))
                except Exception:
                    pass

                def _gen_single(idx):
                    try:
                        card = script_data["characters_with_images"][idx]
                        char = card["char_data"]
                        image_label = card["image_label"]
                        user_prompt = card["prompt_textbox"].get("1.0", tk.END).strip() # Get text from ScrolledText
                        
                        full_prompt = char.get("image_prompt") or user_prompt
                        create_result = create_image(project_id, access_token, idx, full_prompt, log=output_text)

                        # Process result and update GUI
                        if isinstance(create_result, dict):
                            image_url = create_result.get('image_uri') or create_result.get('uri') or None
                            if not image_url and create_result.get('raw_response'):
                                try:
                                    rr = create_result.get('raw_response')
                                    candidate = find_media_uri(rr)
                                    if candidate:
                                        image_url = candidate
                                except Exception:
                                    pass
                            
                            if image_url:
                                def update_gui():
                                    load_and_display_image(image_url, image_label)
                                    if card.get("status_label"):
                                        card["status_label"].config(text="Đã gen", fg=ACCENT)
                                    notification.show_notification(frame, f"✓ {char.get('name')} đã gen xong", type_="success")
                                    increment_completed()
                                
                                frame.after(0, update_gui)
                                return
                            
                            # Check for inline/base64
                            b = find_base64_image(create_result)
                            if b:
                                def update_gui_inline():
                                    display_image_from_bytes(b, image_label)
                                    if card.get("status_label"):
                                        card["status_label"].config(text="Đã gen", fg=ACCENT)
                                    notification.show_notification(frame, f"✓ {char.get('name')} đã gen xong (inline)", type_="success")
                                    increment_completed()
                                
                                frame.after(0, update_gui_inline)
                                return

                        # If no URL found, mark as error
                        def update_gui_error():
                            image_label.config(text="[Không có uri]", fg="#ef4444")
                            if card.get("status_label"):
                                card["status_label"].config(text="Lỗi gen", fg="#ef4444")
                            increment_completed()
                        
                        frame.after(0, update_gui_error)
                        
                    except Exception as e:
                        def update_gui_exception():
                            image_label.config(text=f"[Lỗi]\n{str(e)[:30]}")
                            if card.get("status_label"):
                                card["status_label"].config(text="Lỗi gen", fg="#ef4444")
                            increment_completed()
                        
                        frame.after(0, update_gui_exception)

                threading.Thread(target=_gen_single, args=(i,), daemon=True).start()
                time.sleep(0.3)

        threading.Thread(target=_gen_all, daemon=True).start()


    def generate_script():
        """Generate script in background thread"""
        try:
            num_scenes = int(scenes_var.get())
            num_chars = int(chars_var.get())
            anim_style = style_var.get()
        except ValueError:
            notification.show_notification(frame, "✗ Vui lòng nhập số hợp lệ", type_="failed")
            return

        status_label.config(text="⏳ Đang tạo kịch bản...")
        # Disable retry while a generation is in progress
        try:
            retry_btn.config(state=tk.DISABLED)
        except Exception:
            pass
        frame.update_idletasks()

        def _generate():
            try:
                result = generate_script_service.generate_fairy_tale_script(
                    num_scenes=num_scenes,
                    num_characters=num_chars
                )
                
                # Store script data
                script_data["script"] = result
                
                # Debug: log how many characters original script returned
                try:
                    orig_chars = len(result.get('characters', [])) if isinstance(result, dict) else 0
                    output_text.config(state=tk.NORMAL)
                    output_text.insert(tk.END, f"\nFound {orig_chars} original characters in script.\n")
                    output_text.config(state=tk.DISABLED)
                except Exception:
                    pass

                # Enhance with animation style if no error
                if "error" not in result:
                    enhanced = generate_character_service.generate_characters_from_script(result, animation_style=anim_style)
                    if enhanced.get("characters"):
                        result["characters_enhanced"] = enhanced["characters"]
                        try:
                            output_text.config(state=tk.NORMAL)
                            output_text.insert(tk.END, "\n== Enhanced Characters ==\n")
                            output_text.insert(tk.END, json.dumps(enhanced["characters"], ensure_ascii=False, indent=2))
                            output_text.insert(tk.END, f"\n== Total Characters: {len(enhanced['characters'])} ==\n")
                            output_text.config(state=tk.DISABLED)
                        except Exception:
                            pass
                        
                        frame.update_idletasks()
                        
                        def populate_on_main():
                            populate_character_cards(enhanced["characters"])
                            # Log after population
                            try:
                                output_text.config(state=tk.NORMAL)
                                output_text.insert(tk.END, f"\n[v0] Character cards populated: {len(script_data.get('characters_with_images', []))} cards created\n")
                                output_text.config(state=tk.DISABLED)
                            except Exception:
                                pass
                            # Auto-generate images after cards are visible
                            frame.after(500, generate_all_images)
                        
                        frame.after(0, populate_on_main)
                    else:
                        try:
                            output_text.config(state=tk.NORMAL)
                            output_text.insert(tk.END, "\n[v0] WARNING: No characters in enhanced result\n")
                            output_text.config(state=tk.DISABLED)
                        except Exception:
                            pass
                        notification.show_notification(frame, "✗ Không có nhân vật để hiển thị", type_="failed")
                else:
                    error_msg = result.get("error", "Unknown error")
                    
                    # Handle quota errors (surface message and enable retry)
                    if "quota" in error_msg.lower():
                        msg = error_msg
                        # Parse suggested wait seconds if present
                        import re
                        m = re.search(r"Please retry in\s*(\d+)", msg)
                        wait_secs = None
                        if m:
                            try:
                                wait_secs = int(m.group(1))
                            except Exception:
                                wait_secs = None

                        status_label.config(text="❌ Quota exceeded")
                        try:
                            output_text.config(state=tk.NORMAL)
                            output_text.insert(tk.END, f"\nQuota error encountered: {msg}\n")
                            output_text.insert(tk.END, "Please check billing, reduce request rate, or wait before retrying.\n")
                            output_text.config(state=tk.DISABLED)
                        except Exception:
                            pass

                        # Enable retry button: if wait_secs is specified, start countdown
                        def enable_retry_after(s):
                            try:
                                retry_btn.config(state=tk.DISABLED)
                                count = s
                                def tick():
                                    nonlocal count
                                    if count <= 0:
                                        retry_btn.config(state=tk.NORMAL, command=generate_script)
                                        try:
                                            output_text.config(state=tk.NORMAL)
                                            output_text.insert(tk.END, "Retry enabled. Click 'Thử lại' to retry.\n")
                                            output_text.config(state=tk.DISABLED)
                                        except Exception:
                                            pass
                                        return
                                    # Update status_label with countdown
                                    try:
                                        status_label.config(text=f"❌ Quota - retry in {count}s")
                                    except Exception:
                                        pass
                                    count -= 1
                                    frame.after(1000, tick)
                                tick()
                            except Exception:
                                retry_btn.config(state=tk.NORMAL, command=generate_script)

                        if wait_secs:
                            enable_retry_after(wait_secs)
                        else:
                            retry_btn.config(state=tk.NORMAL, command=generate_script)
                
                json_output = json.dumps(result, ensure_ascii=False, indent=2)
                
                output_text.config(state=tk.NORMAL)
                output_text.delete(1.0, tk.END)
                output_text.insert(tk.END, json_output)
                output_text.config(state=tk.DISABLED)

                if "error" not in result:
                    status_label.config(text="✅ Tạo thành công! Bạn có thể quay lại tạo lại")
                    retry_btn.config(state=tk.DISABLED)
                    notification.show_notification(frame, "✅ Kịch bản đã được tạo thành công!", type_="success", duration=4000)
                else:
                    status_label.config(text=f"❌ {result['error']}")
                    notification.show_notification(frame, f"✗ Lỗi: {result['error']}", type_="failed")
            except Exception as e:
                err = str(e)
                status_label.config(text=f"❌ {err}")
                # If exception message contains quota, surface retry
                if 'quota' in err.lower() or 'quota exceeded' in err.lower():
                    try:
                        output_text.config(state=tk.NORMAL)
                        output_text.insert(tk.END, f"\nException quota error: {err}\n")
                        output_text.config(state=tk.DISABLED)
                    except Exception:
                        pass
                    retry_btn.config(state=tk.NORMAL, command=generate_script)
                notification.show_notification(frame, f"✗ Lỗi: {err}", type_="failed")

        # Run in background thread
        thread = threading.Thread(target=_generate, daemon=True)
        thread.start()

    def export_json():
        """Export script as JSON file"""
        if not script_data["script"] or "error" in script_data["script"]:
            notification.show_notification(frame, "✗ Không có dữ liệu để export", type_="failed")
            return

        try:
            from pathlib import Path
            output_path = Path("generated_script.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(script_data["script"], f, ensure_ascii=False, indent=2)
            notification.show_notification(frame, f"✓ Đã lưu: {output_path}", type_="success")
        except Exception as e:
            notification.show_notification(frame, f"✗ Lỗi lưu file: {str(e)}", type_="failed")

    # Set the generate button command
    gen_btn.config(command=generate_script)

    return frame

def download_video(encoded_video, output_path, log):
    """Download và save video từ encoded string.
    
    Args:
        encoded_video: Base64 encoded video string
        output_path: Đường dẫn file output
        log: Widget tkinter để hiển thị log
        
    Returns:
        str: Đường dẫn file đã save
    """
    import base64
    import os
    from datetime import datetime
    
    log.insert("end", "\n💾 Đang save video...\n")
    
    try:
        # Decode base64
        video_data = base64.b64decode(encoded_video)
        
        # Tạo filename với timestamp nếu cần
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"video_{timestamp}.mp4"
        
        # Đảm bảo thư mục tồn tại
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write file
        with open(output_path, 'wb') as f:
            f.write(video_data)
        
        file_size = os.path.getsize(output_path)
        log.insert("end", f"✅ Video saved: {output_path}\n")
        log.insert("end", f"📊 File size: {file_size / 1024 / 1024:.2f} MB\n")
        
        return output_path
        
    except Exception as e:
        log.insert("end", f"❌ Save error: {str(e)}\n")
        return None

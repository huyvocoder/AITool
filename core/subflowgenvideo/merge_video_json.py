def merge_video_json(media_generation_ids):
    """Tạo JSON body để concatenate videos.
    
    Args:
        media_generation_ids: List of media generation IDs
        
    Returns:
        dict: JSON body cho concatenate API
    """
    input_videos = []
    
    for media_id in media_generation_ids:
        if media_id:  # Skip None values
            input_videos.append({
                "mediaGenerationId": media_id,
                "lengthNanos": 8000,  # 8 seconds
                "startTimeOffset": "0.000000000s",
                "endTimeOffset": "8.000000000s"
            })
    
    return {
        "requestInput": {
            "inputVideos": input_videos
        }
    }

import requests
import json


def call_ark_api(image_url, text, api_key="5e406c6c-60b1-4842-be32-9b9964068792", model="doubao-seed-1-8-251228"):
    """
    Call the Ark API with image and text inputs
    
    Args:
        image_url (str): URL of the input image
        text (str): Text prompt
        api_key (str): API key for authorization
        model (str): Model identifier
    
    Returns:
        dict: Response from the API
    """
    url = "https://ark.cn-beijing.volces.com/api/v3/responses"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": image_url
                    },
                    {
                        "type": "input_text",
                        "text": text
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    # Example usage
    image_url = "https://ark-project.tos-cn-beijing.volces.com/doc_image/ark_demo_img_1.png"
    text = "你看见了什么？"
    
    result = call_ark_api(image_url, text)
    
    if result:
        print("API Response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Failed to get a response from the API")
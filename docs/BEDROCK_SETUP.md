# 🚀 AWS Bedrock Setup Guide

## 🔑 **Step 1: Set Up Your AWS Credentials**

### **Option A: Local Development (.streamlit/secrets.toml)**

1. **Edit the secrets file** (already created and gitignored):
```bash
nano "/Users/hetalksinmaths/adversarial demo/.streamlit/secrets.toml"
```

2. **Add your AWS credentials**:
```toml
[aws]
AWS_ACCESS_KEY_ID = "AKIA..."  # Your actual access key
AWS_SECRET_ACCESS_KEY = "..."  # Your actual secret key  
AWS_DEFAULT_REGION = "us-east-1"  # Change if different

[bedrock]
BEDROCK_REGION = "us-east-1"  # Region where you have Bedrock access

[models]
CLAUDE_OPUS = "anthropic.claude-3-opus-20240229-v1:0"
CLAUDE_SONNET = "anthropic.claude-3-5-sonnet-20241022-v2:0"  
CLAUDE_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"
```

### **Option B: AWS CLI Configuration**
```bash
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key  
# Enter your region (e.g., us-east-1)
# Enter output format (json)
```

## 🌍 **Step 2: Enable Bedrock Model Access**

1. **Go to AWS Console**: [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. **Navigate to**: Model access → Manage model access
3. **Enable**: Anthropic Claude models:
   - ✅ Claude 3 Opus
   - ✅ Claude 3.5 Sonnet  
   - ✅ Claude 3 Haiku
4. **Submit** request (usually approved instantly)

## 💰 **Step 3: Check Your Credits**

In AWS Billing Dashboard, verify you have:
- Bedrock service credits
- Sufficient limits for API calls

## 🧪 **Step 4: Test Local Integration**

Run your local Streamlit to test:

```bash
cd "/Users/hetalksinmaths/adversarial demo"
source streamlit-env/bin/activate
streamlit run streamlit_app.py --server.port 8501
```

The app will now:
- ✅ **Use real Claude models** for generation
- ✅ **Fallback to simulation** if API fails  
- ✅ **Show connection status** in the UI

## 🌐 **Step 5: Streamlit Cloud Deployment**

For production deployment, add secrets to Streamlit Cloud:

1. **Go to**: [share.streamlit.io](https://share.streamlit.io)
2. **Find your app**: aqumen-demo
3. **Click**: Settings ⚙️
4. **Secrets tab**: Add the same content from your local `.streamlit/secrets.toml`
5. **Save** and the app will redeploy with real API integration

## 📊 **What Changes in Your Demo:**

### **Before (Simulated)**:
- Fixed 2-3 second delays
- Predetermined responses
- No real AI interaction

### **After (Real Bedrock)**:
- ✅ **Dynamic content generation**
- ✅ **Real model responses** 
- ✅ **Actual adversarial testing**
- ✅ **Unique questions each time**
- ✅ **True model differentiation**

## 🔧 **Available Regions for Bedrock:**
- `us-east-1` (N. Virginia) - Most models available
- `us-west-2` (Oregon)  
- `eu-west-1` (Ireland)
- `ap-southeast-1` (Singapore)
- `ap-northeast-1` (Tokyo)

## 🚨 **Security Notes:**

✅ **Safe**: Secrets are gitignored and never committed  
✅ **Local**: `.streamlit/secrets.toml` stays on your machine  
✅ **Cloud**: Streamlit Cloud encrypts secrets  
✅ **Rotation**: You can rotate AWS keys anytime  

## 💡 **Pro Tips:**

1. **Start with Haiku** for testing (cheapest)
2. **Monitor costs** in AWS Billing Dashboard
3. **Set billing alerts** for usage tracking
4. **Use IAM roles** for production (more secure than keys)

## 🎯 **Ready to Go Live:**

Once configured, your demo will showcase:
- **Real AI model capabilities**
- **Dynamic question generation**  
- **Authentic model differentiation**
- **Professional-grade API integration**

Perfect for impressing in interviews, client demos, or research presentations! 🚀
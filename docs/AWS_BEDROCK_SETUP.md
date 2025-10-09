# 🚀 AWS Bedrock Setup Guide - Complete Walkthrough

## 📋 **Prerequisites**

Before starting, ensure you have:
- ✅ AWS Account with billing enabled
- ✅ Bedrock credits or payment method configured
- ✅ Basic understanding of AWS Console navigation

## 🎯 **Step 1: AWS Account Setup**

### **1.1 Sign into AWS Console**
1. **Go to**: [aws.amazon.com](https://aws.amazon.com)
2. **Click**: "Sign In to the Console"  
3. **Use**: Your AWS root account or IAM user

### **1.2 Check Your Region**
1. **Top right corner**: Ensure you're in a Bedrock-supported region
2. **Recommended regions**:
   - `us-east-1` (N. Virginia) - Most models available
   - `us-west-2` (Oregon)
   - `eu-west-1` (Ireland)

## 🔑 **Step 2: Request Model Access (CRITICAL)**

### **2.1 Navigate to Bedrock Console**
1. **AWS Console search**: Type "Bedrock" → Click "Amazon Bedrock"
2. **Or direct link**: [console.aws.amazon.com/bedrock](https://console.aws.amazon.com/bedrock)

### **2.2 Enable Model Access**
1. **Left sidebar**: Click "Model access"
2. **Top right**: Click "Manage model access" button
3. **Select models**:
   - ✅ **Anthropic**: Check "Claude 3 Opus"
   - ✅ **Anthropic**: Check "Claude 3.5 Sonnet"  
   - ✅ **Anthropic**: Check "Claude 3 Haiku"
   - ✅ **Anthropic**: Check "Claude 3.5 Haiku" (if available)

4. **Click**: "Request model access"
5. **Status**: Should show "Access granted" within minutes (usually instant)

### **2.3 Verify Access**
- **Status should show**: 🟢 "Access granted" for all Claude models
- **If pending**: Wait 5-10 minutes and refresh

## 🔐 **Step 3: Create API Credentials**

### **3.1 Create IAM User (Recommended for Security)**
1. **AWS Console**: Search "IAM" → Click "Identity and Access Management"
2. **Users**: Click "Users" in left sidebar
3. **Create user**: Click "Create user" button
4. **User details**:
   - **User name**: `aqumen-demo`
   - **Access type**: ✅ "Programmatic access"
5. **Click**: "Next: Permissions"

### **3.2 Attach Bedrock Permissions**
1. **Permission options**: Choose "Attach policies directly"
2. **Search**: Type "bedrock"
3. **Select**: ✅ `AmazonBedrockFullAccess`
   - *For production: Use more restrictive permissions*
4. **Click**: "Next: Tags" (skip tags)
5. **Click**: "Next: Review"
6. **Click**: "Create user"

### **3.3 Get Your API Keys**
1. **After user creation**: You'll see a success page
2. **IMPORTANT**: Download the CSV or copy:
   - **Access Key ID**: `AKIA...` (starts with AKIA)
   - **Secret Access Key**: Long string of random characters
3. **⚠️ WARNING**: This is your ONLY chance to see the secret key!

## 🛠️ **Step 4: Test Bedrock Access**

### **4.1 Install AWS CLI (Optional but Recommended)**
```bash
# macOS
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Verify installation
aws --version
```

### **4.2 Configure AWS CLI**
```bash
aws configure
# Enter your Access Key ID: AKIA...
# Enter your Secret Access Key: ...
# Enter region: us-east-1
# Enter output format: json
```

### **4.3 Test API Access**
```bash
# List available models
aws bedrock list-foundation-models --region us-east-1

# Test Claude Haiku (cheapest for testing)
aws bedrock-runtime invoke-model \
  --region us-east-1 \
  --model-id anthropic.claude-3-haiku-20240307-v1:0 \
  --cli-binary-format raw-in-base64-out \
  --body '{"anthropic_version": "bedrock-2023-05-31", "max_tokens": 100, "messages": [{"role": "user", "content": "Hello, respond with just the word SUCCESS if you can see this."}]}' \
  output.json

# Check the result
cat output.json
```

## 📝 **Step 5: Configure Your Demo**

### **5.1 Update Local Secrets File**
```bash
cd "/Users/hetalksinmaths/adversarial demo"
nano .streamlit/secrets.toml
```

### **5.2 Add Your Credentials**
```toml
[aws]
AWS_ACCESS_KEY_ID = "AKIA..."  # Your actual access key from Step 3.3
AWS_SECRET_ACCESS_KEY = "..."  # Your actual secret key from Step 3.3  
AWS_DEFAULT_REGION = "us-east-1"  # Change if you used different region

[bedrock]
BEDROCK_REGION = "us-east-1"  # Same as above

[models]
# Official model IDs from Anthropic documentation
CLAUDE_OPUS = "anthropic.claude-3-opus-20240229-v1:0"
CLAUDE_SONNET = "anthropic.claude-3-5-sonnet-20241022-v2:0"  
CLAUDE_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"
```

### **5.3 Test Local Demo**
```bash
cd "/Users/hetalksinmaths/adversarial demo"
source streamlit-env/bin/activate
pip install boto3
streamlit run streamlit_app.py --server.port 8501
```

**Expected result**: Should show 🚀 **LIVE MODE**: Connected to AWS Bedrock

## 🌐 **Step 6: Deploy to Streamlit Cloud**

### **6.1 Add Secrets to Streamlit Cloud**
1. **Go to**: [share.streamlit.io](https://share.streamlit.io)
2. **Find your app**: aqumen-demo
3. **Click**: Settings ⚙️ (gear icon)
4. **Secrets tab**: Paste the same content from your local `.streamlit/secrets.toml`
5. **Save**: App will automatically redeploy

### **6.2 Verify Deployment**
- **Visit**: https://aqumen-demo.streamlit.app/
- **Look for**: 🚀 **LIVE MODE** banner at top
- **Test**: Enter a topic and see real API generation!

## 💰 **Step 7: Monitor Costs**

### **7.1 Set Up Billing Alerts**
1. **AWS Console**: Search "Billing" → "Billing and Cost Management"  
2. **Budgets**: Create budget for Bedrock usage
3. **Recommended**: $5-10 monthly budget for demos

### **7.2 Monitor Usage**
- **Bedrock Console**: Check usage metrics
- **Cost per model**: Haiku (cheapest) → Sonnet → Opus (most expensive)
- **Typical demo cost**: $0.10-0.50 per session

## 🔍 **Step 8: Verification Checklist**

### ✅ **AWS Console Verification:**
- [ ] Bedrock model access shows "Access granted" for Claude models
- [ ] IAM user created with Bedrock permissions
- [ ] API keys downloaded and secured
- [ ] Region supports Bedrock (us-east-1 recommended)

### ✅ **Local Demo Verification:**
- [ ] `.streamlit/secrets.toml` configured with real credentials
- [ ] Demo shows "LIVE MODE" status
- [ ] Can enter topics and get dynamic responses
- [ ] No API errors in logs

### ✅ **Streamlit Cloud Verification:**
- [ ] Secrets added to cloud deployment
- [ ] Public demo shows "LIVE MODE"
- [ ] Real-time question generation working
- [ ] Models respond with unique content each time

## 🚨 **Common Issues & Solutions**

### **❌ "Access denied" errors**
- **Solution**: Check model access in Bedrock console
- **Wait**: Sometimes takes 10-15 minutes for permissions to propagate

### **❌ "Region not supported" errors**  
- **Solution**: Switch to us-east-1 region in AWS console and secrets file

### **❌ "Invalid credentials" errors**
- **Solution**: Regenerate IAM user access keys
- **Check**: Ensure no extra spaces/characters in secrets.toml

### **❌ "Quota exceeded" errors**
- **Solution**: Request quota increase in AWS Service Quotas console
- **Or**: Use Haiku model (has higher default limits)

## 🎉 **Success Indicators**

When everything is working correctly:

### **Local Demo:**
- ✅ Shows "🚀 LIVE MODE: Connected to AWS Bedrock"
- ✅ Questions generate with unique, contextual content  
- ✅ Different model responses in adversarial attempts
- ✅ No simulation fallback messages

### **Cloud Demo:**
- ✅ https://aqumen-demo.streamlit.app/ shows LIVE MODE
- ✅ Public users can experience real AI generation
- ✅ Professional-grade demo ready for sharing

## 💡 **Pro Tips**

1. **Start with Haiku**: Test with cheapest model first
2. **Monitor costs**: Set up billing alerts early
3. **Use regions wisely**: us-east-1 has most model availability
4. **Secure credentials**: Never commit secrets to git
5. **Test thoroughly**: Try different topics to verify dynamic generation

## 🔗 **Useful Links**

- [Anthropic Bedrock Docs](https://docs.anthropic.com/en/api/claude-on-amazon-bedrock)
- [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
- [IAM Users Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users.html)
- [Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)

## 🌐 **Streamlit Cloud Deployment**

### **Deploy Your Demo Permanently**

#### **Step 1: Push to GitHub**
```bash
cd "/path/to/adversarial demo"

# Ensure .gitignore excludes secrets
echo ".streamlit/secrets.toml" >> .gitignore
echo ".env" >> .gitignore

# Commit and push
git add .
git commit -m "Ready for Streamlit Cloud deployment"
git push origin main
```

#### **Step 2: Deploy on Streamlit Cloud**
1. **Go to**: [share.streamlit.io](https://share.streamlit.io)
2. **Sign in** with GitHub account
3. **Click**: "New app"
4. **Repository**: Select your repo
5. **Branch**: `main`
6. **Main file path**: `backend/streamlit_app.py`
7. **Advanced settings**: Add secrets (see below)
8. **Click**: "Deploy!"

#### **Step 3: Configure Secrets in Streamlit Cloud**
In the Streamlit Cloud dashboard:
1. **Go to**: App settings → Secrets
2. **Add your secrets** in TOML format:

```toml
[aws]
AWS_ACCESS_KEY_ID = "your-access-key"
AWS_SECRET_ACCESS_KEY = "your-secret-key"
AWS_DEFAULT_REGION = "us-east-1"

[models]
CLAUDE_OPUS = "anthropic.claude-3-opus-20240229-v1:0"
CLAUDE_SONNET = "anthropic.claude-3-5-sonnet-20240620-v1:0"  
CLAUDE_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"
```

#### **Step 4: Your Demo Goes Live**
Your demo will be available at:
```
https://share.streamlit.io/yourusername/repo-name/main/backend/streamlit_app.py
```

### **Streamlit Cloud Benefits**
- ✅ **Always Available** - No local server needed
- ✅ **Mobile Responsive** - Works on any device
- ✅ **Automatic Updates** - Deploys on git push
- ✅ **Free Hosting** - Perfect for demos and prototypes
- ✅ **Secure Secrets** - Environment variables protected
- ✅ **Zero Setup** - Users just need the URL

## 🔮 **Next Steps**

### **Deployment Strategy:**
```
Local Development → GitHub → Streamlit Cloud → Production Ready
```

### **Troubleshooting Deployment:**
- **Streamlit Issues**: Check app logs in Streamlit Cloud dashboard
- **Import Errors**: Ensure all dependencies in requirements.txt
- **Secrets Not Working**: Verify TOML format and restart app

---

🎯 **Ready to showcase your professional AI demo with real Claude models!** 🚀
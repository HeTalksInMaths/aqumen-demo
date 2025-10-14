# Adversarial Example Evaluation Rubric

## Part A: OUTPUT QUALITY RUBRIC
*Evaluates the final adversarial question and its educational value*

### Scoring Criteria (1-5 scale, 5 = excellent)

#### 1. **Conceptual Depth** (Weight: 25%)
- **5**: Tests fundamental theoretical understanding of domain concepts
- **4**: Tests important conceptual knowledge with some depth
- **3**: Tests conceptual understanding but somewhat surface-level
- **2**: Tests basic concepts with limited depth
- **1**: Tests trivial or syntax-level knowledge

#### 2. **Subtlety & Adversarial Quality** (Weight: 20%)
- **5**: Error looks completely reasonable to non-experts, very hard to spot
- **4**: Error appears logical but has subtle domain-specific issues
- **3**: Error is somewhat subtle but detectable with careful analysis
- **2**: Error is noticeable but might be overlooked
- **1**: Error is obvious or syntactic

#### 3. **Production Impact** (Weight: 20%)
- **5**: Causes critical system failures, significant business impact
- **4**: Causes major performance or reliability issues
- **3**: Causes moderate problems that affect user experience
- **2**: Causes minor issues or inefficiencies
- **1**: Minimal or no real-world impact

#### 4. **Expert Differentiation Potential** (Weight: 15%)
- **5**: Strong models will definitely catch it, weak models will definitely miss it
- **4**: High likelihood of clear differentiation between model capabilities
- **3**: Good chance of differentiation with some uncertainty
- **2**: Possible differentiation but not guaranteed
- **1**: Unclear if models would differentiate consistently

#### 5. **Educational Value** (Weight: 10%)
- **5**: Teaches critical domain concepts that practitioners must understand
- **4**: Teaches important concepts with good learning outcomes
- **3**: Teaches useful concepts with moderate learning value
- **2**: Teaches basic concepts with limited learning value
- **1**: Minimal educational benefit

#### 6. **Realistic Context** (Weight: 10%)
- **5**: Based on actual production scenarios developers encounter
- **4**: Realistic scenario that could occur in practice
- **3**: Somewhat realistic but simplified
- **2**: Contrived but plausible scenario
- **1**: Unrealistic or toy example

**Output Score = (Conceptual Depth × 0.25) + (Subtlety × 0.20) + (Production Impact × 0.20) + (Expert Differentiation × 0.15) + (Educational Value × 0.10) + (Realistic Context × 0.10)**

---

## Part B: PIPELINE DEMONSTRATION RUBRIC
*Evaluates how well the example showcases the full 7-step adversarial pipeline*

### Scoring Criteria (1-5 scale, 5 = excellent)

#### 1. **Difficulty Category Sophistication** (Weight: 15%)
- **5**: Shows clear skill progression with time indicators and detailed competency levels
- **4**: Good skill differentiation with some progression indicators
- **3**: Basic skill levels with adequate differentiation
- **2**: Simple categorization with minimal depth
- **1**: Trivial or unclear difficulty categories

#### 2. **Error Catalog Quality** (Weight: 20%)
- **5**: Comprehensive domain-specific errors with production impact, likelihood, and difficulty ratings
- **4**: Good domain errors with most metadata present
- **3**: Adequate error identification with some metadata
- **2**: Basic errors with minimal context
- **1**: Generic or poorly defined errors

#### 3. **Model Differentiation Clarity** (Weight: 20%)
- **5**: Crystal clear why strong model succeeds and weak model fails - demonstrates exact knowledge gap
- **4**: Good differentiation with clear reasoning
- **3**: Adequate differentiation with some explanation
- **2**: Unclear differentiation or weak reasoning
- **1**: No clear differentiation demonstrated

#### 4. **Judgment System Sophistication** (Weight: 15%)
- **5**: Detailed confidence scoring, domain expertise evaluation, and clear success criteria
- **4**: Good evaluation with most sophistication elements
- **3**: Adequate judgment with basic confidence measures
- **2**: Simple pass/fail with minimal analysis
- **1**: Poor or missing judgment logic

#### 5. **Student Assessment Transformation** (Weight: 15%)
- **5**: Excellent pedagogical design with tight error spans and clear learning objectives
- **4**: Good educational transformation with solid span design
- **3**: Adequate student question with basic spans
- **2**: Simple transformation with loose spans
- **1**: Poor educational design or unclear spans

#### 6. **Pipeline Flow Coherence** (Weight: 15%)
- **5**: Each step builds logically on previous, creating coherent narrative from topic to assessment
- **4**: Good flow with most steps connecting well
- **3**: Adequate flow with some logical connections
- **2**: Basic flow but some disconnected steps
- **1**: Poor flow or disconnected pipeline steps

**Pipeline Score = (Difficulty × 0.15) + (Error Catalog × 0.20) + (Model Differentiation × 0.20) + (Judgment × 0.15) + (Student Assessment × 0.15) + (Flow Coherence × 0.15)**

---

## Part C: COMBINED EVALUATION

### **Overall Excellence Score**
**Final Score = (Output Quality × 0.60) + (Pipeline Demonstration × 0.40)**

### **Score Ranges:**
- **4.5-5.0**: **GOLD STANDARD** - Perfect demo example, showcases full system power
- **4.0-4.4**: **EXCELLENT** - Strong demo with minor improvements needed
- **3.5-3.9**: **GOOD** - Solid demo but needs refinement for showcase
- **3.0-3.4**: **FAIR** - Adequate but not demo-ready without significant work
- **Below 3.0**: **POOR** - Needs major revision for any use

### **Bonus Criteria (+0.2 each):**
- **Cutting-edge relevance**: Based on 2024-2025 DeepLearning.AI course material
- **Industry pain point**: Addresses common misconception in Gen AI development
- **Theoretical foundation**: Error reveals fundamental misunderstanding of AI concepts
- **Demo storytelling**: Creates compelling narrative for showcasing system capabilities

### **Penalty Criteria (-0.2 each):**
- **Too narrow**: Overly specific to one framework rather than conceptual
- **Documentation error**: More about reading docs than domain expertise
- **Outdated context**: Uses deprecated or old practices
- **Unclear pipeline**: Steps don't clearly demonstrate the adversarial methodology

## Evaluation Focus Questions

### For Output Quality:
1. Would a domain expert immediately recognize this as a sophisticated assessment?
2. Does the error test real expertise vs. superficial knowledge?
3. Would this question be valuable in a professional evaluation context?

### For Pipeline Demonstration:
1. Does this example clearly show why the 7-step pipeline is necessary?
2. Would a non-expert understand the power of the adversarial approach from this example?
3. Does each pipeline step add clear value to the final result?
4. Would this convince stakeholders of the system's sophistication?

---

## Usage Instructions

1. **Evaluate each example** using both rubrics
2. **Calculate scores** for Output Quality and Pipeline Demonstration
3. **Compute Final Score** using the weighted combination
4. **Apply bonus/penalty points** based on additional criteria
5. **Select highest-scoring example** as the gold standard for hardcoded demo
6. **Document reasoning** for why the winning example best showcases the system
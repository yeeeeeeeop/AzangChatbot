# Chatbot practice

#### All the files on this repository is owned by devRestain.   


---
What to do   
번역 모델 확인 - api, llm, prompt...   
목표 test set을 만들어 정량적 평가 대비   
GPT-3.5 넣어서 성능 확인   
진단 알고리즘 조정   

---
UI에 등장하는 메세지들을 고치고 싶으면 utils/messages의 UI messages class의 class 변수인 dict에 조정   
form은 UI messages class의 class 변수 __system_messages_dict["form"]를 조정하면 설정 가능   
llm 프롬프트를 고치고 싶으면 llm/prompts를 조정하면 설정 가능   

---
gpt 답변 예시   
**Official Diagnostic Letter**

Dear Caregiver,

Based on the symptoms described for your baby, along with the comments provided by medical professionals, the following possible diagnoses could be considered:

1. **Necrotizing Enterocolitis (NEC):**
   - Symptoms: Black stool, diarrhea, fever, low appetite, tiredness.
   - Context: Association with gastrointestinal illness, specifically NEC, in premature infants.
   - Recommendation: Seek immediate medical attention for proper evaluation and management.

2. **Gastrointestinal Infection (Possibly Bacterial or Viral):**
   - Symptoms: Black stool, diarrhea, fever, low appetite, tiredness.
   - Context: Mention of various enteropathogens causing diarrhea in infants.
   - Recommendation: Consult a healthcare provider for appropriate treatment and to prevent dehydration.

3. **Rotavirus Infection:**
   - Symptoms: Black stool, diarrhea, fever, low appetite, tiredness.
   - Context: Prevalence of rotavirus infections in children with acute gastroenteritis.
   - Recommendation: Monitor the baby closely and seek medical attention for management.

4. **Biliary Atresia:**
   - Symptoms: Black stool, fever, low appetite, tiredness.
   - Context: Screening system for early detection of biliary atresia.
   - Recommendation: Immediate medical attention for further evaluation and management.

It is crucial to act promptly and follow the recommendations provided by healthcare professionals. Ensure the baby stays hydrated and comfortable while awaiting medical evaluation. If the symptoms worsen or new ones appear, do not hesitate to seek urgent medical care.

Take care of the baby and provide a nurturing environment for their well-being.

Warm regards,

[Medical Institution Name]
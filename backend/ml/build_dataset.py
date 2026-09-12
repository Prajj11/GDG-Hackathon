"""Build a comprehensive, multi-turn, multilingual dataset for Digital Guardrails.
Covers English, Hindi, Hinglish, Malayalam, and Manglish.
Target: 450 balanced, realistic multi-turn conversation windows.
44.4% Neutral (benign, gaming banter, homework, safety advice, negations).
"""
import json
import csv
from pathlib import Path

DATASET_JSON = Path('backend/ml/dataset.json')
DATASET_CSV = Path('backend/ml/dataset.csv')

# Canonical labels requested by the user
LABEL_MAP = {
    'grooming_trust_building': 'grooming-trust-building',
    'grooming_isolation_request': 'grooming-isolation-request',
    'grooming_coercive_language': 'grooming-coercive-language',
    'bullying_harassment': 'bullying-harassment',
    'neutral': 'neutral',
}

import re
from backend.ml.fetch_real_datasets import detect_script, fetch_all_real_data

def create_dataset():
    data = []
    cid = 1

    def add(lang, label, risk, turns, notes=""):
        nonlocal cid
        conv_id = f"synth_{cid:04d}"
        cid += 1
        normalized_turns = []
        for t in turns:
            if isinstance(t, (list, tuple)):
                normalized_turns.append({"speaker": t[0], "text": t[1]})
            elif isinstance(t, dict):
                normalized_turns.append(t)
        window_text = " \n ".join([f"{t['speaker']}: {t['text']}" for t in normalized_turns])
        target_text = normalized_turns[-1]['text'] if len(normalized_turns) > 0 else ""
        script = detect_script(window_text, lang)
        data.append({
            "conversation_id": conv_id,
            "language": lang,
            "script": script,
            "pattern_label": label,
            "pattern_type_canonical": LABEL_MAP[label],
            "risk_level": risk,
            "turns": normalized_turns,
            "window_text": window_text,
            "target_text": target_text,
            "source_dataset": "Synthetic-Grooming-PAN12",
            "origin": "synthetic",
            "rationale": notes or f"Multi-turn synthetic conversation illustrating {label}."
        })

    # =========================================================================
    # 1. NEUTRAL (Target: 200 examples across English, Hindi, Hinglish, Malayalam, Manglish)
    # Subcategories: School & Study, Gaming Banter, Family & Friends, Protective Safety Advice, Negation & Reported Speech
    # =========================================================================

    # English - School / Study / Sports (15)
    english_school = [
        ([("A", "Did you understand question 4 in math?"), ("B", "Not really, it was quite confusing."), ("A", "Let us work on our homework together tomorrow during lunch.")], "homework collaboration"),
        ([("A", "Are you coming to science club today?"), ("B", "Yes, Mr. Sharma said we are building circuits."), ("A", "Cool, see you in the physics lab at 4 PM.")], "school club"),
        ([("A", "Don't forget tomorrow is sports day!"), ("B", "I got my white sneakers ready."), ("A", "Good luck in the 100m relay sprint!")], "sports day"),
        ([("A", "Who has the English literature notes?"), ("B", "I took notes on chapter 3."), ("A", "Can you please share them in the official class group?")], "study notes"),
        ([("A", "Great job on the history presentation today."), ("B", "Thanks! I was so nervous standing in front of everyone."), ("A", "You did awesome, teacher gave our team full marks.")], "presentation praise"),
        ([("A", "Are we having the chemistry test on Friday?"), ("B", "Yes, teacher confirmed it covers acids and bases."), ("A", "Okay, let us prepare notes tonight.")], "exam reminder"),
        ([("A", "Did you submit the art assignment?"), ("B", "I just finished watercolor painting."), ("A", "Nice, let's submit it before the bell rings.")], "art project"),
        ([("A", "Is the library open after school today?"), ("B", "Yes, until 5 PM."), ("A", "Great, let's borrow the reference books together.")], "library study"),
        ([("A", "Can you bring your extra calculator tomorrow?"), ("B", "Sure, I have two."), ("A", "Thanks a lot, see you in the morning.")], "school supplies"),
        ([("A", "Are we practicing for annual day dance?"), ("B", "Yes, third period in the auditorium."), ("A", "Don't forget the costume guidelines teacher sent.")], "annual day dance"),
        ([("A", "Did you get selected for the debate team?"), ("B", "Yes, the topic is renewable energy."), ("A", "Awesome! Let's research arguments together.")], "debate prep"),
        ([("A", "Where are we meeting for the group project?"), ("B", "At the school cafeteria after classes."), ("A", "Perfect, please tell your parents where we are meeting.")], "parent notice for meeting"),
        ([("A", "How did your piano recital go?"), ("B", "It was fun, my mom took a video."), ("A", "Congratulations, you practiced really hard!")], "recital"),
        ([("A", "Are you joining the summer coding workshop?"), ("B", "Yes, my dad registered me yesterday."), ("A", "Awesome, we can learn Python together.")], "coding workshop"),
        ([("A", "Good morning! Did bus route 12 change?"), ("B", "No, it arrives at the usual 7:30 AM stop."), ("A", "Thanks, see you at the bus stop.")], "school bus"),
    ]
    for turns, note in english_school:
        add("English", "neutral", "Low", turns, note)

    # English - Gaming Banter & Slang (10)
    english_gaming = [
        ([("A", "Dude you completely destroyed me in that match!"), ("B", "Haha your sniper shot missed by an inch."), ("A", "That game was killer, let's play another round tonight.")], "gaming slang benign"),
        ([("A", "I got a new game for my birthday. Want to play online with our friends?"), ("B", "Which game is it?"), ("A", "Minecraft! I set up a private multiplayer world for our class.")], "multiplayer birthday game"),
        ([("A", "Bro you're dead! Watch out behind you!"), ("B", "Revive me, revive me!"), ("A", "I got you, good win team!")], "in-game combat callouts"),
        ([("A", "Your rank in Valorant is insane!"), ("B", "Thanks, played five competitive games yesterday."), ("A", "Carry me to Gold rank this weekend please!")], "game ranking"),
        ([("A", "Noob move dropping the flag there!"), ("B", "My ping was 300ms, total lag."), ("A", "All good, next round we crush them.")], "friendly gamer teasing"),
        ([("A", "That boss battle took two hours to beat!"), ("B", "Did you get the legendary drop?"), ("A", "Yes, finally got the dragon shield.")], "boss fight"),
        ([("A", "Are you streaming the tournament tonight?"), ("B", "Just watching on Twitch with my brother."), ("A", "Let's watch together on voice chat.")], "watching esports"),
        ([("A", "GG guys, well played!"), ("B", "Nice defense on point B."), ("A", "See you tomorrow for the weekend cup.")], "good game"),
        ([("A", "He totally wrecked our squad with that grenade."), ("B", "Next time stay spread out."), ("A", "Yeah lesson learned.")], "squad loss review"),
        ([("A", "Who wants to trade duplicate Pokemon cards tomorrow?"), ("B", "I have Charizard!"), ("A", "Bring your binder to lunch recess.")], "trading cards"),
    ]
    for turns, note in english_gaming:
        add("English", "neutral", "Low", turns, note)

    # English - Protective Safety Advice & Quotations & Negations (15)
    english_safety = [
        ([("A", "Some random account messaged me on Roblox asking where I live."), ("B", "That's super weird!"), ("A", "I blocked them and showed my mom immediately.")], "safety action"),
        ([("A", "Teacher said never share personal phone numbers or passwords online."), ("B", "Yeah our cyber safety class was really helpful."), ("A", "Always tell a trusted adult if someone makes you uncomfortable.")], "safety advice"),
        ([("A", "Coach told us to never share private details with strangers online."), ("B", "Did someone ask you?"), ("A", "No, just standard rules for the team group chat.")], "coach advice"),
        ([("A", "Remember: never send private photos or keep secrets from your family."), ("B", "Yes, my parents have the family safety guidelines."), ("A", "Good, stay safe online.")], "guidelines"),
        ([("A", "My friend told me a stranger messaged: Send your photo or I will report you."), ("B", "Did your friend report it?"), ("A", "Yes, they reported the account and told school counselor.")], "reported speech"),
        ([("A", "I am not threatening you and I do not want your private details."), ("B", "I know, just checking what the homework assignment was."), ("A", "Page 45 exercises 1 to 10.")], "negation of threat"),
        ([("A", "Someone posted: I will destroy your reputation."), ("B", "Where was that?"), ("A", "It was an example of cyberbullying in our civics textbook.")], "textbook example"),
        ([("A", "The surprise party for Rahul is a secret until Saturday."), ("B", "Don't worry, nobody will tell him."), ("A", "His parents are bringing the cake at 5 PM.")], "benign birthday secret"),
        ([("A", "I forgot my lunch money today."), ("B", "I have an extra sandwich, let's share!"), ("A", "Thank you so much, you are a lifesaver.")], "sharing lunch"),
        ([("A", "Can you ask your mom if you can come over to bake cookies?"), ("B", "She said yes as long as your mom is home."), ("A", "Awesome, my mom bought chocolate chips.")], "parent confirmed playdate"),
        ([("A", "If anyone online ever asks you to keep secrets, tell a teacher right away."), ("B", "Our school counselor gave us helpline stickers today."), ("A", "Yeah, 1098 is for child safety.")], "helpline awareness"),
        ([("A", "Don't click that link in the group chat, it looks like spam."), ("B", "Good catch, I almost clicked it."), ("A", "Let's ask the admin to delete the message.")], "spam warning"),
        ([("A", "My dad helped me set my Instagram account to private."), ("B", "Smart move, only friends should see posts."), ("A", "Yeah, no random strangers allowed.")], "privacy settings"),
        ([("A", "We are organizing a charity book drive this weekend."), ("B", "I have lots of old storybooks to donate."), ("A", "Bring them to the school auditorium on Friday.")], "charity drive"),
        ([("A", "I am not angry with you at all."), ("B", "I thought you were upset about the score."), ("A", "Not at all, it was just a tough referee call.")], "negation of anger"),
    ]
    for turns, note in english_safety:
        add("English", "neutral", "Low", turns, note)

    # Hindi - School / Study / Everyday (15)
    hindi_school = [
        ([("A", "आज स्कूल कैसा था?"), ("B", "बहुत अच्छा, विज्ञान में नया प्रयोग किया।"), ("A", "चलो शाम को मिलकर होमवर्क करते हैं।")], "homework"),
        ([("A", "कल गणित की परीक्षा की तैयारी हो गई?"), ("B", "त्रिकोणमिति थोड़ी मुश्किल लग रही है।"), ("A", "मैं तुम्हें आसान तरीके से समझा दूंगा, लाइब्रेरी में मिलते हैं।")], "math prep"),
        ([("A", "मम्मी पापा को बताकर दोस्तों के साथ पार्क में खेलने आना।"), ("B", "हाँ, मैंने माँ से पूछ लिया है।"), ("A", "ठीक है, शाम 5 बजे क्रिकेट खेलेंगे।")], "parent permission"),
        ([("A", "हिंदी के प्रोजेक्ट की फाइल तैयार हो गई?"), ("B", "चित्र लगाना बाकी है बस।"), ("A", "कल सुबह स्कूल में असेंबली से पहले जमा करना है।")], "project deadline"),
        ([("A", "आज इतिहास वाले सर ने क्या पढ़ाया?"), ("B", "मुगल काल के बारे में चर्चा हुई थी।"), ("A", "मुझे अपनी कॉपी दे देना, मैं नोट्स बना लूंगा।")], "class notes"),
        ([("A", "क्या कल स्कूल की छुट्टी है?"), ("B", "हाँ, त्योहार की वजह से अवकाश है।"), ("A", "अच्छा हुआ, पेंडिंग असाइनमेंट पूरा हो जाएगा।")], "holiday notice"),
        ([("A", "ड्राइंग कॉम्पिटिशन में भाग ले रहे हो?"), ("B", "हाँ, पर्यावरण दिवस पर पेंटिंग बनाऊंगा।"), ("A", "बहुत बढ़िया विचार है, शुभकामनाएं!")], "competition"),
        ([("A", "आज लंच में क्या लाए हो?"), ("B", "माँ ने पनीर के पराठे बनाए हैं।"), ("A", "अरे वाह, दोनों मिलकर शेयर करेंगे।")], "lunch sharing"),
        ([("A", "बस स्टॉप पर कितनी देर में पहुंचोगे?"), ("B", "पाँच मिनट में निकल रहा हूँ।"), ("A", "जल्दी आओ, स्कूल बस आने वाली है।")], "bus stop"),
        ([("A", "वार्षिक उत्सव में कौन सा गाना गा रहे हो?"), ("B", "देशभक्ति गीत की तैयारी चल रही है।"), ("A", "प्रैक्टिस के लिए संगीत कक्ष में चलना।")], "music practice"),
        ([("A", "क्या तुम्हें कल का होमवर्क समझ आया?"), ("B", "सर ने जो ब्लैकबोर्ड पर लिखा था वो नोट किया है।"), ("A", "शुक्रिया, मैं अभी लिख लेता हूँ।")], "blackboard notes"),
        ([("A", "शाम को बैडमिंटन खेलने चलोगे?"), ("B", "माँ से पूछकर बताता हूँ।"), ("A", "हाँ, बिना बताए कहीं मत जाना।")], "ask parents first"),
        ([("A", "कंप्यूटर लैब में नया सॉफ्टवेयर इंस्टॉल हुआ है।"), ("B", "स्क्रैच प्रोग्रामिंग सीखेंगे अब।"), ("A", "हाँ, गेम बनाना बहुत मजेदार होगा।")], "computer lab"),
        ([("A", "मेरे पास साइंस की अतिरिक्त किताब है।"), ("B", "क्या मैं दो दिन के लिए पढ़ सकता हूँ?"), ("A", "बिल्कुल, कल स्कूल ले आऊंगा।")], "book sharing"),
        ([("A", "आज पीटीआई सर ने नई एक्सरसाइज सिखाई।"), ("B", "हाँ, योग दिवस की तैयारी करवा रहे थे।"), ("A", "सुबह जल्दी उठने की आदत अच्छी है।")], "physical training"),
    ]
    for turns, note in hindi_school:
        add("Hindi", "neutral", "Low", turns, note)

    # Hindi - Protective Guidance & Negations (15)
    hindi_safety = [
        ([("A", "टीचर ने कहा है इंटरनेट पर किसी अनजान से अपनी जानकारी साझा मत करना।"), ("B", "हाँ, कल की कार्यशाला में यही सिखाया था।"), ("A", "अगर कोई परेशान करे तो तुरंत माता-पिता को बताना चाहिए।")], "safety advice"),
        ([("A", "किसी अनजान व्यक्ति को अपनी तस्वीर या पता कभी मत भेजना।"), ("B", "हाँ, मेरी दीदी ने भी यही समझाया है।"), ("A", "सुरक्षित रहना सबसे ज्यादा जरूरी है।")], "stranger warning"),
        ([("A", "मैं तुम्हें कोई धमकी नहीं दे रहा हूँ।"), ("B", "मुझे लगा तुम नाराज हो।"), ("A", "नहीं भाई, सिर्फ खेल का स्कोर बता रहा था।")], "negation threat"),
        ([("A", "मेरे दोस्त ने मुझे जन्मदिन पर सुंदर पेन गिफ्ट किया।"), ("B", "बहुत प्यारा पेन है।"), ("A", "हम सबने क्लास में टॉफियां बांटी।")], "benign birthday gift"),
        ([("A", "सरप्राइज पार्टी के बारे में राहुल को मत बताना।"), ("B", "चिंता मत करो, शाम को सबको सरप्राइज देंगे।"), ("A", "उसके माता-पिता को हमने पहले ही बता दिया है।")], "surprise party"),
        ([("A", "एक अनजान नंबर से मैसेज आया था।"), ("B", "तुमने क्या किया?"), ("A", "मैंने तुरंत पापा को दिखाया और नंबर ब्लॉक कर दिया।")], "blocked stranger"),
        ([("A", "साइबर हेल्पलाइन का नंबर 1930 और बच्चों के लिए 1098 है।"), ("B", "स्कूल की डायरी में भी लिखा हुआ है।"), ("A", "हाँ, यह जानकारी सबको पता होनी चाहिए।")], "helpline knowledge"),
        ([("A", "हम ऑनलाइन गेम में टीम बनाकर खेल रहे थे।"), ("B", "अपोजिट टीम बहुत अच्छी थी।"), ("A", "हाँ, उन्होंने हमें मैच में हरा दिया लेकिन मजा आया।")], "game loss"),
        ([("A", "सोशल मीडिया पर अपनी लोकेशन कभी शेयर नहीं करनी चाहिए।"), ("B", "सही बात है, इससे प्राइवेसी बनी रहती है।"), ("A", "हमेशा सतर्क रहना चाहिए।")], "privacy caution"),
        ([("A", "मैंने कोई गलत काम नहीं किया है।"), ("B", "मुझे तुम पर पूरा भरोसा है दोस्त।"), ("A", "चलो सच-सच टीचर को बता देते हैं।")], "telling truth"),
        ([("A", "घर के बड़ों से कोई भी जरूरी बात छुपानी नहीं चाहिए।"), ("B", "हाँ, माँ हमेशा सही सलाह देती हैं।"), ("A", "किसी भी संकोच के बिना बात करनी चाहिए।")], "open communication"),
        ([("A", "क्या तुमने नया पासवर्ड सेट किया?"), ("B", "हाँ, ऐसा जो किसी को आसानी से पता न चले।"), ("A", "बहुत अच्छा, अपना पासवर्ड कभी दोस्तों को भी मत दो।")], "password security"),
        ([("A", "खेलते वक्त चोट तो नहीं लगी?"), ("B", "थोड़ा घुटना छिल गया था।"), ("A", "फर्स्ट एड बॉक्स से दवाई लगा ली ना? ध्यान रखा करो।")], "caring friend"),
        ([("A", "क्या हम सब मिलकर ग्रुप स्टडी करें?"), ("B", "हाँ, शनिवार दोपहर को सब मेरे घर आ जाओ।"), ("A", "सबके माता-पिता से अनुमति ले ली है।")], "group study with permission"),
        ([("A", "उसने खेल में मुझे पूरी तरह पछाड़ दिया।"), ("B", "अरे अगली बार तुम जीतोगे!"), ("A", "हाँ, खेल भावना से खेलना चाहिए।")], "gaming defeat benign"),
    ]
    for turns, note in hindi_safety:
        add("Hindi", "neutral", "Low", turns, note)

    # Hinglish - School, Gaming Slang, Everyday Chat (25)
    hinglish_neutral = [
        ([("A", "Kal homework saath mein karte hain?"), ("B", "Haan chalega, mere ghar aaja."), ("A", "Done, mummy ko bhi bata diya hai maine.")], "homework parent told"),
        ([("A", "Aaj match mast tha yaar, tune pura game carry kiya!"), ("B", "Haha clutch moment mein bach gaya."), ("A", "Kal squad match mein milte hain.")], "gaming slang"),
        ([("A", "Aaj game killer tha yaar, tune mujhe match mein destroy kar diya!"), ("B", "Bhai wo headshot lucky tha."), ("A", "Next round mein revenge match hoga.")], "benign killer destroy slang"),
        ([("A", "Teacher ne bola koi photo maange toh mat bhejna aur parents ko batana."), ("B", "Sahi bola, online strangers se door hi rehna chahiye."), ("A", "Always safe side rehna better hai.")], "safety advice"),
        ([("A", "Main dhamki nahi de raha aur mujhe tumhari private details nahi chahiye."), ("B", "Acha mujhe laga serious baat hai."), ("A", "Arrey chill, bas science notes maang raha tha.")], "explicit threat negation"),
        ([("A", "Group chat mein address mat likho kisi ka."), ("B", "Haan privacy rules follow karte hain."), ("A", "Project ki details direct call pe discuss kar lenge.")], "group privacy"),
        ([("A", "Birthday surprise ki planning alag group mein karte hain."), ("B", "Haan Rohan ko pata nahi chalna chahiye."), ("A", "Sabke parents ko already invite bhej diya hai.")], "surprise party parents aware"),
        ([("A", "Bro tuition kitne baje khatam hogi?"), ("B", "Around 6 PM, physics sir test le rahe hain."), ("A", "Theek hai, bahar wait karunga.")], "tuition wait"),
        ([("A", "Ye formula samajh nahi aa raha trigonometry ka."), ("B", "Ruk video call pe screen share karke samjhata hoon."), ("A", "Thanks bhai, life bacha li.")], "study help"),
        ([("A", "Kal PT dress pehen ke aana hai kya?"), ("B", "Haan Wednesday hai na, white uniform."), ("A", "Shit mera badge kho gaya, extra hai kya?"), ("B", "Haan spare badge le aaunga.")], "school uniform"),
        ([("A", "Exam center ka admit card download kiya?"), ("B", "Haan papa ne printout nikaal diya."), ("A", "Principal ke sign karwane honge kal.")], "admit card"),
        ([("A", "Bhai canteen mein samosa khayenge?"), ("B", "Mere paas lunch box hai mummy ne banaya."), ("A", "Chal share kar lete hain dono.")], "canteen lunch"),
        ([("A", "Kal match mein umpire ne dead ball declare kar diya tha."), ("B", "Haan clearly wide thi ball."), ("A", "Koi nahi, agla tournament jeetenge.")], "cricket discussion"),
        ([("A", "Bhai internet pe random logon ko accept mat kiya kar."), ("B", "Haan meri profile private hi hai."), ("A", "Good, unknown friend requests decline kar diya kar.")], "cyber caution"),
        ([("A", "Meri behen ne mujhe nayi cycle gift ki pass hone par."), ("B", "Arrey congratulations yaar!"), ("A", "Kal subah ride pe chalte hain colony mein.")], "benign cycle gift"),
        ([("A", "Bhai class mein sabka roast ho gaya aaj."), ("B", "Sir ne sabko stand up karwaya assignment na karne pe."), ("A", "Haha ab kal tak complete karna padega.")], "teacher scolding benign"),
        ([("A", "Kisi unknown site pe apna number mat daalna."), ("B", "Haan phishing scam ho sakta hai."), ("A", "Teacher ne cyber security week mein bataya tha.")], "phishing warning"),
        ([("A", "Yaar ye level itna hard hai, main 10 baar mar chuka hoon!"), ("B", "Left side se dodge kar ke jump mar."), ("A", "Wah trick kaam kar gayi, checkpoint mil gaya!")], "gaming retry"),
        ([("A", "Tu mere saath library chal raha hai kya?"), ("B", "Mummy se permission leke 10 minute mein batata hoon."), ("A", "Haan permission leke hi aana.")], "library with permission"),
        ([("A", "Tune school bus miss kar di kya?"), ("B", "Haan subah late utha tha, papa drop kar rahe hain."), ("A", "First period se pehle pohach jana.")], "missed bus"),
        ([("A", "Roblox pe mere sath class group banaye?"), ("B", "Haan bas class ke bache hone chahiye usme."), ("A", "Bilkul, no outsiders allowed.")], "gaming class group"),
        ([("A", "Sports teacher bol rahe the inter-school football trials hain."), ("B", "Tu striker position ke liye try kar."), ("A", "Haan practice karni padegi roz sham ko.")], "football trials"),
        ([("A", "Kisine class desk pe ink gira di."), ("B", "Monitor ko bol ke safai karwao."), ("A", "Haan teacher ke aane se pehle theek karte hain.")], "classroom incident"),
        ([("A", "Main kal class nahi aa paunga, fever hai."), ("B", "Get well soon bhai!"), ("A", "Notes ki photo bhej dena sham ko."), ("B", "Haan pakka bhej dunga, aaram kar.")], "illness notes"),
        ([("A", "Cyber crime helpline number 1930 note kar le."), ("B", "Haan phone mein save kar liya."), ("A", "Koi bhi fraud ho toh turant report karna chahiye.")], "helpline note"),
    ]
    for turns, note in hinglish_neutral:
        add("Hinglish", "neutral", "Low", turns, note)

    # Malayalam - School, Family, Safety, Benign Banter (20)
    malayalam_neutral = [
        ([("A", "ഇന്ന് സ്കൂൾ എങ്ങനെ ഉണ്ടായിരുന്നു?"), ("B", "നല്ല ദിവസമായിരുന്നു, കണക്ക് പരീക്ഷ എളുപ്പമായിരുന്നു."), ("A", "നമുക്ക് വൈകുന്നേരം ഒരുമിച്ച് ഇരുന്ന് പഠിക്കാം.")], "school day"),
        ([("A", "അമ്മയോട് ചോദിച്ചിട്ട് കളിക്കാൻ വരൂ."), ("B", "അമ്മ സമ്മതിച്ചു, 5 മണിക്ക് ഗ്രൗണ്ടിൽ എത്താം."), ("A", "ബാറ്റും പന്തും ഞാൻ കൊണ്ടുവരാം.")], "parent permission"),
        ([("A", "ആരെങ്കിലും നിന്നെ ശല്യം ചെയ്താൽ ഉടൻ അധ്യാപകനോട് പറയണം."), ("B", "അതെ, സ്കൂളിൽ കൗൺസിലർ അങ്ങനെ പറഞ്ഞിട്ടുണ്ട്."), ("A", "എപ്പോഴും സുരക്ഷിതമായിരിക്കണം.")], "safety advice"),
        ([("A", "നാളെ നമുക്ക് കൂട്ടുകാരോടൊപ്പം പ്രോജക്ട് ചെയ്യാം."), ("B", "എവിടെയാണ് ഒത്തുകൂടുന്നത്?"), ("A", "സ്കൂൾ ലൈബ്രറിയിൽ വെച്ച് ചെയ്യാം.")], "project study"),
        ([("A", "നിന്റെ അനുവാദമില്ലാതെ ചിത്രങ്ങൾ ആരുമായും പങ്കിടില്ല."), ("B", "ശരി, എനിക്ക് താല്പര്യമില്ലെങ്കിൽ ഫോട്ടോ എടുക്കേണ്ട."), ("A", "തീർച്ചയായും, നിന്റെ സ്വകാര്യത ഞാൻ ബഹുമാനിക്കുന്നു.")], "respect privacy"),
        ([("A", "സ്കൂളിലെ പരിപാടിയുടെ ചിത്രങ്ങൾ ഗ്രൂപ്പിൽ ഇടുന്നതിന് മുമ്പ് എല്ലാവരുടെയും സമ്മതം ചോദിക്കാം."), ("B", "അതാണ് നല്ല മര്യാദ."), ("A", "അതെ, എല്ലാവരുടെയും അനുമതി വേണം.")], "photo consent"),
        ([("A", "സ്വകാര്യ വിവരങ്ങൾ അപരിചിതരുമായി പങ്കിടരുത്."), ("B", "അതെ, ഓൺലൈനിൽ ജാഗ്രത വേണം."), ("A", "വിശ്വാസമുള്ള മുതിർന്നവരോട് എപ്പോഴും കാര്യങ്ങൾ പറയണം.")], "online caution"),
        ([("A", "ഇന്നത്തെ ഫുട്ബോൾ കളി വളരെ ആവേശകരമായിരുന്നു!"), ("B", "നിങ്ങൾ അടിച്ച ഗോൾ മനോഹരമായിരുന്നു."), ("A", "നല്ല ടീം വർക്ക് ഉണ്ടായിരുന്നു.")], "football match"),
        ([("A", "ഓണത്തിന് സ്കൂളിൽ പൂക്കളം ഇടാൻ പൂക്കൾ വാങ്ങണ്ടേ?"), ("B", "നാളെ രാവിലെ എല്ലാവരും പൂക്കൾ കൊണ്ടുവരാൻ ടീച്ചർ പറഞ്ഞു."), ("A", "ഞാൻ ചെണ്ടുമല്ലി പൂക്കൾ കൊണ്ടുവരാം.")], "onam festival"),
        ([("A", "നാളെ സയൻസ് എക്സിബിഷൻ ഉണ്ട്, മോഡൽ റെഡിയായോ?"), ("B", "വോൾക്കാനോ മോഡൽ പൂർത്തിയായി."), ("A", "അടിപൊളി, സമ്മാനം കിട്ടാൻ സാധ്യതയുണ്ട്.")], "science exhibition"),
        ([("A", "കമ്പ്യൂട്ടർ പരീക്ഷയ്ക്ക് എന്തൊക്കെ പഠിക്കണം?"), ("B", "ആദ്യത്തെ മൂന്ന് ചാപ്റ്ററുകൾ."), ("A", "ശരി, ഇന്ന് രാത്രി റിവിഷൻ ചെയ്യാം.")], "exam revision"),
        ([("A", "അപരിചിതരിൽ നിന്ന് ചോക്ലേറ്റോ സമ്മാനങ്ങളോ വാങ്ങരുത്."), ("B", "അമ്മ എപ്പോഴും അത് ഓർമ്മിപ്പിക്കാറുണ്ട്."), ("A", "അതെ, അപരിചിതരെ സൂക്ഷിക്കണം.")], "stranger gift warning"),
        ([("A", "ക്ലാസ് പിക്കിനിക്കിന് എങ്ങോട്ടാണ് പോകുന്നത്?"), ("B", "വാണ്ടർലായിലേക്ക് ആണെന്ന് ടീച്ചർ പറഞ്ഞു."), ("A", "വീട്ടിൽ അനുവാദം ചോദിക്കണം ആദ്യം.")], "picnic permission"),
        ([("A", "നിന്റെ സൈക്കിൾ ഒന്നു തരുമോ, കടയിൽ പോകാൻ?"), ("B", "എടുത്തോളൂ, സൂക്ഷിച്ച് ഓടിക്കണം."), ("A", "താങ്ക്സ്, പത്ത് മിനിറ്റിൽ തിരികെ തരാം.")], "borrow bicycle"),
        ([("A", "ഓൺലൈൻ ഗെയിമിൽ അപരിചിതർ മെസ്സേജ് അയച്ചാൽ എന്തുചെയ്യും?"), ("B", "ഉടൻ ബ്ലോക്ക് ചെയ്യുകയും അച്ഛനോട് പറയുകയും ചെയ്യും."), ("A", "വളരെ നല്ല കാര്യം.")], "block stranger"),
        ([("A", "ചൈൽഡ് ഹെൽപ്പ് ലൈൻ നമ്പർ 1098 ആണെന്ന് ഓർമ്മയുണ്ടോ?"), ("B", "ഉണ്ട്, ഏത് ആപത്തിലും കുട്ടികൾക്ക് വിളിക്കാം."), ("A", "അതെ, അത് സൗജന്യ നമ്പറാണ്.")], "childline 1098"),
        ([("A", "ഞാൻ നിന്നെ ഭീഷണിപ്പെടുത്തുകയല്ല."), ("B", "എനിക്ക് മനസ്സിലായി, തമാശ പറഞ്ഞതാണെന്ന്."), ("A", "അതെ, നമ്മൾ നല്ല കൂട്ടുകാരാണ്.")], "negation of threat"),
        ([("A", "ഗെയിമിൽ നീ എന്നെ തോൽപ്പിച്ചു കളഞ്ഞല്ലോ!"), ("B", "അടുത്ത തവണ നീ ജയിക്കും, വിഷമിക്കേണ്ട."), ("A", "അതെ, സ്പോർട്സ്മാൻ സ്പിരിറ്റ് വേണം.")], "benign game defeat"),
        ([("A", "സ്കൂൾ ബാഗ് വളരെ ഭാരമുള്ളതാണ് ഇന്ന്."), ("B", "ടൈംടേബിൾ നോക്കി പുസ്തകങ്ങൾ എടുത്താൽ മതി."), ("A", "ശരിയാണ്, ആവശ്യമില്ലാത്ത പുസ്തകങ്ങൾ ഒഴിവാക്കാം.")], "school bag"),
        ([("A", "നമുക്ക് ഒരുമിച്ച് ചെസ്സ് കളിക്കാം."), ("B", "എനിക്ക് നീക്കങ്ങൾ പഠിപ്പിച്ചു തരുമോ?"), ("A", "തീർച്ചയായും, വളരെ എളുപ്പമാണ്.")], "chess game"),
    ]
    for turns, note in malayalam_neutral:
        add("Malayalam", "neutral", "Low", turns, note)

    # Manglish - School, Gaming, Guidance (15)
    manglish_neutral = [
        ([("A", "Naale namukku friends inte koode kalikkam."), ("B", "Ammayodu paranjittu varam."), ("A", "Athe ammayude permission vangittu vaa.")], "ask permission"),
        ([("A", "Homework cheytho?"), ("B", "Maths kurachu baaki undu."), ("A", "Namukku evening call cheythu doubt theerkkam.")], "homework study"),
        ([("A", "Aarenkilum budhimuttichaal teacher nodu parayanam."), ("B", "Athe, cyber cell number schoolil paranju thannittundu."), ("A", "Safe aayi irikkanam online il.")], "safety guidance"),
        ([("A", "Game il nee enne kollam adichu tholppichu!"), ("B", "Haha adutha roundil nee enikku thirichu tharum."), ("A", "Adutha matchil kaanam machane.")], "benign gaming slang"),
        ([("A", "Njan ninne thallaan onnum paranjathalla."), ("B", "Ariyaam da, chumma thamasha paranjathalle."), ("A", "Pinne allathe, nammal best friends alle.")], "negation"),
        ([("A", "Unknown accounts friend request ayachaal accept cheyyaruthu."), ("B", "Njan private account aane vechirikkunnathu."), ("A", "Good, athanu safe.")], "privacy caution"),
        ([("A", "Online class project submit cheytho?"), ("B", "Mail ayachu, teacher reply thannu."), ("A", "Awesome, appol tension theernnu.")], "project submission"),
        ([("A", "Naale school bus time maariyo?"), ("B", "Illa 8 AM nu thanne varum."), ("A", "Ok, morning kaanam.")], "bus time"),
        ([("A", "Birthday gift aayi chechi book tharunnundu."), ("B", "Ethu book aanu?"), ("A", "Harry Potter series, vaayikkan nalla rasama.")], "benign book gift"),
        ([("A", "Drawing competition nu paint box kondu varumo?"), ("B", "Njan extra oil pastels kondu varam."), ("A", "Thanks da, valare upakaram.")], "art supplies"),
        ([("A", "Cyber helpline 1930 note cheytho."), ("B", "Phone il save cheythu vechirikkunnu."), ("A", "Eppozhum ready aayi irikkanam.")], "helpline info"),
        ([("A", "Ente photo aarum share cheyyaruthu please."), ("B", "Illa da, permission illaathe aarum share cheyyilla."), ("A", "Thank you da for understanding.")], "photo consent"),
        ([("A", "Football match il referee wrong foul vilichu."), ("B", "Athu vishayam aakkanda, kalicha reethi nannaayirunnu."), ("A", "Athe, next matchil nammal win cheyyum.")], "match spirit"),
        ([("A", "Tuition sir test paper thanno?"), ("B", "Naale mark parayaam ennu paranju."), ("A", "Full mark kittum ennu vishwasikkaam.")], "tuition test"),
        ([("A", "Veettukaarodu parayaathe engottum pokaruthu."), ("B", "Athe eppozhum ammayodu paranjitte pookarullu."), ("A", "Athanu nallathu.")], "tell family"),
    ]
    for turns, note in manglish_neutral:
        add("Manglish", "neutral", "Low", turns, note)

    # Additional Neutral Examples to reach 45% Neutral ratio (202 / 450)
    extra_english_neutral = [
        ([("A", "Did you practice the violin piece for assembly?"), ("B", "Yes, worked on the second movement yesterday."), ("A", "You sound great, teacher will be proud.")], "music practice"),
        ([("A", "We need one more player for 5-a-side football."), ("B", "Can I join? My shoes are in my locker."), ("A", "Yes please, meet at the turf field in 10 minutes.")], "football team"),
        ([("A", "My sister helped me solve the physics numericals."), ("B", "Physics with vectors is so tough."), ("A", "She explained using diagrams, I can show you tomorrow.")], "peer explanation"),
        ([("A", "Who is bringing snacks for the study group?"), ("B", "My mom packed homemade banana bread."), ("A", "Yum! We will finish the history chapter by 5 PM.")], "study snacks"),
        ([("A", "Did you download the scratch programming assignment?"), ("B", "Yes, made an animation of a jumping cat."), ("A", "That is so cool, show me during computer period.")], "scratch animation"),
        ([("A", "Make sure you wear sunscreen for sports day."), ("B", "Thanks for the reminder, it is going to be hot."), ("A", "Stay hydrated too, bring your water bottle.")], "sports day care"),
        ([("A", "Are we going to the museum field trip on Friday?"), ("B", "Yes, got my permission slip signed by dad."), ("A", "Remember to bring a notebook for the dinosaur exhibit.")], "field trip permission"),
        ([("A", "Good job winning the spelling bee today!"), ("B", "I was so scared on the word 'renaissance'."), ("A", "You spelled it perfectly, congratulations!")], "spelling bee"),
        ([("A", "Did the school bus break down?"), ("B", "A flat tire, mechanic is fixing it now."), ("A", "Teacher called our parents to let them know we will be 20 mins late.")], "bus flat tire"),
        ([("A", "Can you help me set up the microscope in biology?"), ("B", "Sure, make sure the slide is centered."), ("A", "Look, plant cells with chloroplasts! Awesome.")], "biology lab"),
        ([("A", "I forgot my geometry compass today."), ("B", "Here, use my spare one."), ("A", "Thank you, drawing circles without it is impossible.")], "geometry class"),
        ([("A", "What are you reading for English book report?"), ("B", "Percy Jackson and the Lightning Thief."), ("A", "I loved that book! The Greek mythology parts are great.")], "book recommendation"),
        ([("A", "Are you auditioning for the school play?"), ("B", "Trying out for the narrator role."), ("A", "You have a clear voice, you will do great.")], "drama audition"),
        ([("A", "My mom said you can stay for dinner after badminton."), ("B", "Let me call my dad and check first."), ("A", "Sure, tell him dinner will be done by 8 PM.")], "dinner parent call"),
        ([("A", "The robotics team won second place!"), ("B", "Our line-following robot worked without errors."), ("A", "Trophy will be displayed in the principal's office.")], "robotics award"),
    ]
    for turns, note in extra_english_neutral:
        add("English", "neutral", "Low", turns, note)

    extra_hindi_neutral = [
        ([("A", "कल विज्ञान मेले में कौन सा मॉडल लेकर आ रहे हो?"), ("B", "जल संरक्षण पर वर्किंग मॉडल बनाया है।"), ("A", "बहुत उपयोगी विषय है, सबको पसंद आएगा।")], "science fair model"),
        ([("A", "क्या तुमने निबंध प्रतियोगिता की तैयारी की?"), ("B", "स्वच्छ भारत पर निबंध लिख रहा हूँ।"), ("A", "समय सीमा का ध्यान रखना, 500 शब्द होने चाहिए।")], "essay competition"),
        ([("A", "शाम को कॉलोनी के पार्क में साइकिल रेस होगी।"), ("B", "मैं भी अपनी साइकिल लेकर आऊंगा।"), ("A", "हेलमेट पहन कर आना, सुरक्षा पहले है।")], "cycle race safety"),
        ([("A", "आज संस्कृत वाले सर ने बहुत सुंदर श्लोक सिखाया।"), ("B", "हाँ, गुरु की महिमा पर था।"), ("A", "अर्थ भी बहुत गहरा था, डायरी में लिख लिया मैंने।")], "sanskrit shloka"),
        ([("A", "मम्मी ने घर पर गाजर का हलवा बनाया है।"), ("B", "अरे वाह, मुझे भी खिलाओगे?"), ("A", "हाँ टिफिन में लाया हूँ, लंच में साथ खाएंगे।")], "homemade sweet"),
        ([("A", "कल सुबह योग दिवस पर जल्दी आना है स्कूल।"), ("B", "हाँ, सफेद टी-शर्ट और ट्रैक पैंट पहनना है।"), ("A", "योगा मैट भी साथ ले आना।")], "yoga day"),
        ([("A", "क्या तुम्हारे पास अतिरिक्त पेंसिल है?"), ("B", "हाँ, शार्पनर भी ले लो।"), ("A", "धन्यवाद भाई, चित्रकला में काम आएगी।")], "stationery borrow"),
        ([("A", "आज क्रिकेट मैच में तुमने शानदार कैच पकड़ा!"), ("B", "गेंद बहुत तेज आ रही थी, पर हाथ से फिसली नहीं।"), ("A", "उसी कैच से मैच का पासा पलट गया।")], "cricket catch"),
        ([("A", "कक्षा में बोर्ड पर लिखी तारीख सही कर दो कोई।"), ("B", "हाँ, आज 15 तारीख है।"), ("A", "चौक से लिख दिया मैंने।")], "classroom date"),
        ([("A", "दादाजी ने मुझे आज पंचतंत्र की कहानी सुनाई।"), ("B", "कछुए और खरगोश वाली?"), ("A", "नहीं, शेर और समझदार खरगोश की। बहुत सीख मिली।")], "storytelling"),
        ([("A", "हम सब मिलकर पौधे लगाने का अभियान चला रहे हैं।"), ("B", "मैंने घर से नीम का पौधा मंगाया है।"), ("A", "स्कूल के पीछे वाले बगीचे में लगाएंगे।")], "tree plantation"),
        ([("A", "मौसम कितना सुहावना है आज।"), ("B", "हाँ, हल्की-हल्की बारिश हो रही है।"), ("A", "छाता संभाल कर रखना, भीग मत जाना।")], "rainy day"),
        ([("A", "गणित के सर ने कल टेस्ट लेने को कहा है।"), ("B", "अध्याय 5 और 6 का रिवीजन कर लेते हैं।"), ("A", "हाँ, सूत्र याद करने जरूरी हैं।")], "math revision"),
        ([("A", "क्या तुमने बाल दिवस के नाटक में हिस्सा लिया?"), ("B", "हाँ, मैं स्वतंत्रता सेनानी का रोल कर रहा हूँ।"), ("A", "डायलॉग याद हो गए सारे? बहुत खूब!")], "childrens day play"),
        ([("A", "मेरे पिताजी ने नया एटलस ला कर दिया है।"), ("B", "भारत के सभी राज्यों की राजधानियां देखें?"), ("A", "चलो मानचित्र का अध्ययन करते हैं।")], "geography study"),
    ]
    for turns, note in extra_hindi_neutral:
        add("Hindi", "neutral", "Low", turns, note)

    extra_hinglish_neutral = [
        ([("A", "Kal tuition test mein full marks aaye mere!"), ("B", "Party kab de raha hai phir?"), ("A", "Kal school canteen mein samosa meri taraf se.")], "tuition celebration"),
        ([("A", "Chess tournament ke liye register kiya tune?"), ("B", "Haan under-14 category mein."), ("A", "Good luck bhai, opening moves prepare kar le.")], "chess registration"),
        ([("A", "Project ke liye chart paper lena hai market se."), ("B", "School ke pass wali stationary se le lenge."), ("A", "Haan wahan sketch pens bhi mil jayenge.")], "chart paper purchase"),
        ([("A", "PT teacher ne bola warmup exercises daily karni chahiye."), ("B", "Haan body flexible rehti hai."), ("A", "Subah 15 minute running start karte hain kal se.")], "daily running"),
        ([("A", "Yaar chemistry ke chemical equations balance nahi ho rahe."), ("B", "Oxygen count check kar left aur right side pe."), ("A", "Arey haan! Ab balance ho gaya, thank you.")], "chemistry equations"),
        ([("A", "School fest mein food stall lagayein kya?"), ("B", "Haan homemade lemonade aur sandwiches rakhte hain."), ("A", "Teacher se permission letter sign karwana padega pehle.")], "fest food stall"),
        ([("A", "Mere computer mein antivirus expire ho gaya tha."), ("B", "Papa ko bol ke renew karwa le."), ("A", "Haan unhone quick heal update kar diya safe browsing ke liye.")], "antivirus safety"),
        ([("A", "Class group mein faltu forwards mat bheja karo guys."), ("B", "Sahi baat hai, sirf homework discussion hona chahiye."), ("A", "Rules follow karenge toh admin ko problem nahi hogi.")], "group decorum"),
        ([("A", "Kal physics lab mein prism experiment kiya tha."), ("B", "Spectrum of seven colors dikha na?"), ("A", "Haan VIBGYOR pura clear tha wall pe.")], "physics prism"),
        ([("A", "Badminton racket ki gutting toot gayi match mein."), ("B", "Market mein repair ho jati hai 100 rupees mein."), ("A", "Kal sham ko de aaunga dukan pe.")], "racket repair"),
        ([("A", "Social science exhibition ke liye model banaya?"), ("B", "Indus valley civilization ka town planning model hai."), ("A", "The Great Bath include kiya kya? Bohot mast lagega.")], "history model"),
        ([("A", "English teacher ne new novel recommend ki hai reading ke liye."), ("B", "The Blue Umbrella by Ruskin Bond?"), ("A", "Haan, bohot short aur beautiful story hai.")], "reading novel"),
        ([("A", "Subah subah itni thand hai cycle chalaate waqt."), ("B", "Gloves pehan ke aaya kar na."), ("A", "Kal se jacket aur gloves dono pehnunga.")], "winter morning cycle"),
        ([("A", "Inter-house quiz competition kab hai?"), ("B", "Next Friday, current affairs aur general science pe."), ("A", "Newspaper reading start karte hain library mein.")], "quiz preparation"),
        ([("A", "Bhai presentation ke slides ready ho gaye."), ("B", "Font size legible hai na projector screen ke liye?"), ("A", "Haan minimum 24 pt rakha hai sabme.")], "presentation slides"),
    ]
    for turns, note in extra_hinglish_neutral:
        add("Hinglish", "neutral", "Low", turns, note)

    extra_malayalam_neutral = [
        ([("A", "സ്കൂൾ യുവജനോത്സവത്തിൽ കഥാരചനയ്ക്ക് പങ്കെടുക്കുന്നുണ്ടോ?"), ("B", "അതെ, മലയാളം വിഭാഗത്തിൽ പേര് കൊടുത്തു."), ("A", "നല്ലൊരു വിഷയം തെരഞ്ഞെടുത്ത് എഴുതണം, ആശംസകൾ.")], "youth festival"),
        ([("A", "നാളെ ലൈബ്രറി പിരീഡിൽ പുസ്തകം തിരിച്ചേൽപ്പിക്കണം."), ("B", "ഞാൻ ബഷീറിന്റെ 'ബാല്യകാലസഖി' വായിച്ചു തീർത്തു."), ("A", "അടുത്തതായി 'പാത്തുമ്മയുടെ ആട്' എടുക്കാം.")], "malayalam literature"),
        ([("A", "കായികോത്സവത്തിൽ റിലേ ടീമിൽ നീ ഉണ്ടോ?"), ("B", "നാലാമത്തെ ആളായി ഞാൻ ഓടും."), ("A", "ബാറ്റൺ കൈമാറുമ്പോൾ ശ്രദ്ധിക്കണം, വിജയം നമ്മുടെ കൈയിലാണ്.")], "relay race"),
        ([("A", "കമ്പ്യൂട്ടർ ക്ലാസ്സിൽ പൈത്തൺ പ്രോഗ്രാമിംഗ് തുടങ്ങി."), ("B", "ഹലോ വേൾഡ് പ്രിന്റ് ചെയ്യുന്നത് പഠിച്ചു."), ("A", "വളരെ രസകരമാണ് കോഡിംഗ്.")], "python class"),
        ([("A", "പരിസ്ഥിതി ദിനത്തിൽ സ്കൂളിൽ വൃക്ഷത്തൈകൾ വിതരണം ചെയ്യും."), ("B", "ഞാൻ മാവിൻ തൈ വീട്ടിൽ നടാൻ കൊണ്ടുവരും."), ("A", "വെള്ളമൊഴിച്ച് നന്നായി പരിപാലിക്കണം.")], "environment day tree"),
        ([("A", "നാളെ മഴ മുന്നറിയിപ്പ് ഉള്ളതുകൊണ്ട് കുട മറക്കരുത്."), ("B", "റെയിൻകോട്ടും ബാഗിൽ വെച്ചിട്ടുണ്ട്."), ("A", "നനയാതെ സൂക്ഷിക്കണം, ജലദോഷം വരാതെ നോക്കണം.")], "rain caution"),
        ([("A", "ഗണിതശാസ്ത്ര ക്വിസിൽ നമ്മുടെ ക്ലാസിന് ഒന്നാം സ്ഥാനം കിട്ടി!"), ("B", "എല്ലാവരും നന്നായി പരിശ്രമിച്ചു."), ("A", "ടീച്ചർ എല്ലാവർക്കും അഭിനന്ദനങ്ങൾ അറിയിച്ചു.")], "math quiz win"),
        ([("A", "ചിത്രരചനാ മത്സരത്തിൽ വാട്ടർ കളർ ഉപയോഗിക്കാമോ?"), ("B", "അതെ, ഡ്രോയിംഗ് ഷീറ്റ് സ്കൂളിൽ നിന്ന് തരും."), ("A", "നല്ല തീമിൽ വരയ്ക്കണം.")], "painting contest"),
        ([("A", "ക്ലാസ്സിലെ ശുചിത്വ പരിപാലനം ഇന്ന് നമ്മുടെ ഗ്രൂപ്പിനാണ്."), ("B", "ഡെസ്കുകൾ വൃത്തിയാക്കി വേസ്റ്റ് ബിൻ മാറ്റാം."), ("A", "പത്ത് മിനിറ്റിൽ തീർക്കാം.")], "classroom cleaning"),
        ([("A", "സ്കൂൾ ബാന്റ് സെറ്റിൽ ഡ്രംസ് വായിക്കുന്നത് നീയാണോ?"), ("B", "അതെ, എല്ലാ വൈകുന്നേരവും പ്രാക്ടീസ് ഉണ്ട്."), ("A", "റിപ്പബ്ലിക് ദിന പരേഡിൽ കാണാൻ ഭംഗിയുണ്ടാകും.")], "school band"),
        ([("A", "ഹിസ്റ്ററി പ്രോജക്റ്റിന് കേരള ചരിത്രം തെരഞ്ഞെടുത്തു."), ("B", "പഴശ്ശിരാജയുടെ സ്വാതന്ത്ര്യസമര പോരാട്ടങ്ങൾ ഉൾപ്പെടുത്താം."), ("A", "നല്ല ആശയമാണ്, ഫോട്ടോകളും ശേഖരിക്കാം.")], "history project"),
        ([("A", "ലബോറട്ടറിയിൽ ടെസ്റ്റ് ട്യൂബ് പൊട്ടാതെ ശ്രദ്ധിക്കണം."), ("B", "ടീച്ചറുടെ മേൽനോട്ടത്തിൽ മാത്രമേ പരീക്ഷണം ചെയ്യാവൂ."), ("A", "സുരക്ഷാ മുൻകരുതലുകൾ പ്രധാനമാണ്.")], "science lab safety"),
        ([("A", "നാളെ ക്ലാസ് ടെസ്റ്റ് ഉള്ളതുകൊണ്ട് നേരത്തെ ഉറങ്ങണം."), ("B", "രാവിലെ ഉന്മേഷത്തോടെ പരീക്ഷ എഴുതാം."), ("A", "ശുഭരാത്രി, നന്നായി വിശ്രമിക്കൂ.")], "sleep before test"),
        ([("A", "സ്കൂൾ മാഗസിനിലേക്ക് കവിത എഴുതി നൽകിയോ?"), ("B", "പ്രകൃതിയെക്കുറിച്ചുള്ള കവിത അയച്ചു കൊടുത്തു."), ("A", "മാഗസിൻ വരുമ്പോൾ കാണാൻ ആകാംക്ഷയുണ്ട്.")], "magazine poem"),
    ]
    for turns, note in extra_malayalam_neutral:
        add("Malayalam", "neutral", "Low", turns, note)

    extra_manglish_neutral = [
        ([("A", "Coding campil Scratch il game develop cheythu."), ("B", "Enthu type game aanu?"), ("A", "Platformer jumping game, score counter um undu.")], "scratch game"),
        ([("A", "Science lab il microscope il onion cell kandu."), ("B", "Nucleus clear aayi kaanan undaayirunno?"), ("A", "Athe blue stain cheythu nokkiyappol super view.")], "biology microscope"),
        ([("A", "Sports day kku practice cheyyan shoes venam."), ("B", "Running shoes shop il ninnu vaangi."), ("A", "Naale ground il 6 AM nu kaanam.")], "running practice"),
        ([("A", "Class picnic nu Wayanad pokaan plan undu."), ("B", "Tea garden um waterfalls um kaanaam."), ("A", "Ammayude signature permission letteril vaanganam.")], "picnic trip"),
        ([("A", "English teacher book review ezhuthaan paranju."), ("B", "The Alchemist vaayichu review ezhuthi."), ("A", "Simple language il nalla message ulla book aanu.")], "book review"),
        ([("A", "School kalolsavam dance practice thudangiyo?"), ("B", "Oppana dance practice auditorium il undu."), ("A", "Kosthyum order cheythu kazhinju.")], "oppana dance"),
        ([("A", "Chess tournament il second round ethi njan."), ("B", "Super machane, focus cheythu kalikku."), ("A", "Opponent strong aanu, defence nokkanam.")], "chess tournament"),
        ([("A", "Computer screen time kooduthal aakkaruthu."), ("B", "Eye strain aavum ennu doctor paranju."), ("A", "20 minutes kazhiyumbol rest edukkunnathu nallatha.")], "eye health"),
        ([("A", "Social science map drawing easy aano?"), ("B", "India outline mapil rivers mark cheyyan padichu."), ("A", "Himalayan rivers Ganga Brahmaputra clear aanu.")], "map study"),
        ([("A", "Amma lunch boxil vegetable cutlet vechittundu."), ("B", "Wow cutlet ente favourite aanu!"), ("A", "Break timil share cheyyaam namukku.")], "cutlet lunch share"),
        ([("A", "Busil vannekkan varumbo mazha vannu."), ("B", "Kuda undaayirunno kaiyyil?"), ("A", "Athe bagil folded umbrella undaayirunnu, nanjilla.")], "umbrella in rain"),
        ([("A", "Tuition master test paper correct cheythu thannu."), ("B", "Etra mark kitti maths nu?"), ("A", "25 il 23 kitti, calculation mistake poyatha."), ("B", "Adutha pravashyam full mark vangam.")], "test score improvement"),
        ([("A", "Scout and Guides camp weekend il undu."), ("B", "Tent ketti thaamsikkanam alle?"), ("A", "Athe first aid training um knots kettan um padikkum.")], "scout camp"),
    ]
    for turns, note in extra_manglish_neutral:
        add("Manglish", "neutral", "Low", turns, note)


    # =========================================================================
    # 2. GROOMING: TRUST BUILDING (Target: 65 examples)
    # Excessive flattery, gifts, "you are so mature", "only I understand you", building secret bond
    # =========================================================================

    english_trust = [
        ([("A", "You are so mature for your age."), ("B", "Really? Most people treat me like a child."), ("A", "No, you understand things adults don't even get. I want to buy you special gifts.")], "mature flattery gifts"),
        ([("A", "I know we just met online, but you are my favorite person."), ("B", "Thanks, you seem nice too."), ("A", "I will send you free gaming credits and discord nitro if you promise to talk to me every day.")], "exclusive bond credits"),
        ([("A", "Your real-life friends don't truly understand you like I do."), ("B", "Sometimes I feel lonely at school."), ("A", "I'm the only one who cares about your true feelings. Let me spoil you with presents.")], "isolating friendship"),
        ([("A", "You are much more grown up than the other kids your age."), ("B", "That's nice of you to say."), ("A", "I can buy you that new iPhone you wanted, because you deserve special treatment.")], "expensive gift offer"),
        ([("A", "Tell me all your private problems and worries."), ("B", "I usually talk to my parents."), ("A", "Parents don't understand modern youth. Only I truly listen to you, trust me completely.")], "eroding parental trust"),
        ([("A", "You have such a special personality, unlike any student I've seen."), ("B", "Thank you!"), ("A", "I have a special prize just for you. Don't mention it to the other students.")], "favored student pretense"),
        ([("A", "I can transfer 5000 Robux to your account right now."), ("B", "Why would you do that for free?"), ("A", "Because you are special to me, and special friends deserve special rewards.")], "game currency incentive"),
        ([("A", "You don't need to listen to your strict family."), ("B", "They just want me to study."), ("A", "They are holding back your potential. You and I have a connection nobody else can match.")], "driving wedge with family"),
        ([("A", "You look like a model in your profile picture."), ("B", "It's just a school uniform photo."), ("A", "You have natural talent and maturity. Let me mentor you privately.")], "flattery mentoring pretense"),
        ([("A", "I feel like I can tell you secrets I can't tell anyone my age."), ("B", "Aren't you in college though?"), ("A", "Age is just a number, your soul is so mature and wise. We are soulmates.")], "age gap minimization"),
        ([("A", "Did your parents buy you that gaming console?"), ("B", "No, they said it's too expensive."), ("A", "I can order it to a pickup locker for you. Anything for my favorite friend.")], "circumventing parents gift"),
        ([("A", "You are the only person who brings happiness to my life."), ("B", "I'm just a 7th grader."), ("A", "You have a deeper emotional understanding than anyone. I rely on you so much.")], "emotional burden placing"),
        ([("A", "I want to be your protector and guardian angel online."), ("B", "I have my family for that."), ("A", "Your family doesn't see your inner beauty like I do. Let me be your closest confidant.")], "angel pretense"),
    ]
    for turns, note in english_trust:
        add("English", "grooming_trust_building", "Medium", turns, note)

    hindi_trust = [
        ([("A", "तुम अपनी उम्र से बहुत ज्यादा समझदार और मैच्योर हो।"), ("B", "सब मुझे बच्चा समझते हैं वैसे।"), ("A", "नहीं, सिर्फ मैं तुम्हें समझता हूँ। मैं तुम्हें महंगे गिफ्ट्स और फोन दिलाऊंगा।")], "mature flattery"),
        ([("A", "तुम्हारे स्कूल के दोस्त तुम्हारी कद्र नहीं करते।"), ("B", "हाँ, कभी-कभी अकेलापन लगता है।"), ("A", "बस मुझ पर भरोसा रखो। मैं तुम्हारी हर ख्वाहिश पूरी करूंगा।")], "isolating trust"),
        ([("A", "तुम मेरे लिए बहुत खास हो, बाकी सब से अलग।"), ("B", "शुक्रिया भैया।"), ("A", "मैं तुम्हें गेम के डायमंड्स और पैसे दूंगा, बस मुझसे रोज बात किया करो।")], "game credits bond"),
        ([("A", "तुम्हारे माता-पिता तुम्हें समझ नहीं पाते।"), ("B", "वो बहुत रोक-टोक करते हैं।"), ("A", "पुराने खयालात के हैं वो। तुम मुझसे अपनी हर बात शेयर कर सकते हो, मैं जज नहीं करूंगा।")], "parental wedge"),
        ([("A", "तुम्हारी बातें बड़ों जैसी गहरी और समझदारी भरी हैं।"), ("B", "मुझे पढ़ना अच्छा लगता है।"), ("A", "तुम बहुत स्पेशल हो, मैं तुम्हें एक सीक्रेट सरप्राइज गिफ्ट भेजना चाहता हूँ।")], "special reward"),
        ([("A", "मुझे लगता है हमारे बीच एक खास कनेक्शन है।"), ("B", "हम तो अभी ऑनलाइन मिले हैं।"), ("A", "सच्ची दोस्ती में वक्त नहीं देखा जाता। तुम मुझ पर अपनी जान से ज्यादा भरोसा कर सकते हो।")], "instant bond"),
        ([("A", "क्या तुम्हें नया टैबलेट चाहिए ऑनलाइन क्लास के लिए?"), ("B", "मम्मी पापा के पास अभी पैसे नहीं हैं।"), ("A", "मैं खरीद कर दे दूंगा, तुम मेरी सबसे प्यारी दोस्त हो।")], "expensive gift"),
        ([("A", "तुम्हारी प्रोफाइल देख कर लगा तुम बहुत समझदार लड़की हो।"), ("B", "थैंक यू सर।"), ("A", "सर मत कहो, मैं तुम्हारा सबसे अच्छा दोस्त हूँ। तुम्हारी हर मुश्किल सुलझाऊंगा।")], "familiarity trap"),
        ([("A", "दुनिया में सिर्फ मैं तुम्हारी सच्ची परवाह करता हूँ।"), ("B", "घरवाले भी तो हैं।"), ("A", "घरवाले तुम पर पाबंदी लगाते हैं, मैं तुम्हें आजादी और खुशियां दूंगा।")], "freedom promise"),
        ([("A", "तुम मुझसे जो भी मांगोगे मैं फौरन लाकर दूंगा।"), ("B", "आप इतना क्यों कर रहे हैं मेरे लिए?"), ("A", "क्योंकि तुम मेरे दिल के बहुत करीब हो, तुम्हारी खुशी मेरी खुशी है।")], "unwarranted devotion"),
        ([("A", "अपनी सारी परेशानियां मुझे बताया करो।"), ("B", "स्कूल में कुछ बच्चे चिढ़ाते हैं।"), ("A", "मैं हूँ ना तुम्हारे साथ, तुम्हें किसी से डरने की जरूरत नहीं। मैं तुम्हारी रक्षा करूंगा।")], "protector illusion"),
        ([("A", "तुम जितनी खूबसूरत और समझदार हो, वैसा कोई नहीं देखा।"), ("B", "मैं तो बस 13 साल की हूँ।"), ("A", "उम्र मायने नहीं रखती, तुम्हारी समझदारी बड़ों को भी मात देती है।")], "age minimization"),
        ([("A", "तुमने खाना खाया? तुम्हारी बहुत याद आ रही थी।"), ("B", "हाँ खा लिया था।"), ("A", "दिन भर सिर्फ तुम्हारे बारे में सोचता रहता हूँ, तुम मेरी जिंदगी की सबसे खास इंसान हो।")], "obsessive flattery"),
    ]
    for turns, note in hindi_trust:
        add("Hindi", "grooming_trust_building", "Medium", turns, note)

    hinglish_trust = [
        ([("A", "Tum apni age se bahut zyada mature ho yaar."), ("B", "Sach mein? Sab toh bacha samajhte hain."), ("A", "Nahi yaar, unko pata nahi hai. Sirf main tumhe samajhta hoon. Gift bhejun tumhare liye?")], "mature flattery gift"),
        ([("A", "Tumhare school friends jealous hain tumse."), ("B", "Kyu aisa lagta hai aapko?"), ("A", "Kyunki tum special ho. Unko chodo, main tumhe free BGMI skins aur UC dunga.")], "gaming currency incentive"),
        ([("A", "Gharwale tumhari privacy respect nahi karte na?"), ("B", "Haan phone check karte rehte hain."), ("A", "Very bad. Main tumhe ek alag secret phone gift karunga, bas mujhpe trust karo.")], "secret phone offer"),
        ([("A", "Main tumhe apni choti behen jaisa manta hoon par tum bohot mature ho."), ("B", "Thanks bhaiya."), ("A", "Mujhe sab share kiya karo, tumhara aur mera bond sabse strong hona chahiye.")], "pseudo family bond"),
        ([("A", "Yaar tum kitni pretty lagti ho photos mein."), ("B", "Normal photo hi toh hai."), ("A", "Nahi tumhara look models jaisa hai. Main tumhe brand ambassador bana sakta hoon.")], "modeling bait"),
        ([("A", "Tumhari life mein agar koi problem hai toh mujhe batao."), ("B", "Thoda stress hai exams ka."), ("A", "Main tumhara mood fresh karne ke liye shopping gift card bhej raha hoon.")], "financial gift hook"),
        ([("A", "Mujhe lagta hai hum past life mein bhi best friends the."), ("B", "Aisa kuch nahi hota haha."), ("A", "Seriously, tumhare bina mera din nahi guzarta. Only you understand my soul.")], "soul connection flattery"),
        ([("A", "Tumhe pocket money kitni milti hai?"), ("B", "Zyada nahi, bas 200 rupees."), ("A", "Main tumhe har hafte 2000 transfer karunga UPI se, kisi ko batana mat.")], "financial dependency"),
        ([("A", "Tum baki bacho ki tarah childish batein nahi karti."), ("B", "Mujhe deep topics pasand hain."), ("A", "Wahi toh! You are an old soul. We are made for each other's company.")], "intellectual flattery"),
        ([("A", "Tumhari smile bohot cute hai, din ban jata hai dekh ke."), ("B", "Thank you ji."), ("A", "Main chahta hoon tum hamesha khush raho. Jo bologe wo mangwa dunga Amazon se.")], "unconditional gifting trap"),
        ([("A", "Tumhare parents bohot strict hain bechari."), ("B", "Haan dosto ke sath bahar nahi jane dete."), ("A", "Don't worry, main tumhara real support system hoon. Hamesha tumhare sath.")], "parent alienation"),
        ([("A", "Free Fire mein diamond top up karwa doon tumhara?"), ("B", "Bohot mehenga hai wo."), ("A", "Tumhare liye kuch bhi. Bas mujhe voice call pe sweet baatein sunaya karo.")], "grooming exchange"),
        ([("A", "Tum meri life ki sabse favorite person ban chuki ho."), ("B", "Hum toh bas 2 din pehle mile."), ("A", "Connection dil se hota hai time se nahi. Trust me completely.")], "rushing intimacy"),
    ]
    for turns, note in hinglish_trust:
        add("Hinglish", "grooming_trust_building", "Medium", turns, note)

    malayalam_trust = [
        ([("A", "നിന്റെ പ്രായത്തേക്കാൾ പക്വത നിനക്കുണ്ട്."), ("B", "എല്ലാവരും എന്നെ കൊച്ചുകുട്ടിയായിട്ടാണ് കാണുന്നത്."), ("A", "അവർക്ക് നിന്നെ അറിയില്ല. നിന്നെ ഞാൻ മാത്രമേ മനസ്സിലാക്കൂ, നിനക്ക് വിലകൂടിയ സമ്മാനം തരാം.")], "mature flattery gift"),
        ([("A", "നിന്റെ കൂട്ടുകാർക്ക് നിന്നോട് സ്നേഹമില്ല."), ("B", "അവർ ചിലപ്പോൾ എന്നെ ഒഴിവാക്കും."), ("A", "എന്നെ മാത്രം വിശ്വസിക്കൂ. ഞാൻ നിനക്ക് പുതിയ ഫോൺ വാങ്ങിത്തരാം.")], "isolating phone offer"),
        ([("A", "നീ എനിക്ക് വളരെ പ്രത്യേകപ്പെട്ട ആളാണ്."), ("B", "നന്ദി ചേട്ടാ."), ("A", "നിനക്ക് ഓൺലൈൻ ഗെയിമിൽ ഫ്രീ ക്രെഡിറ്റ് തരാം, എന്നോട് മാത്രം സംസാരിച്ചാൽ മതി.")], "exclusive chat gift"),
        ([("A", "വീട്ടുകാർ നിന്റെ സ്വാതന്ത്ര്യം തടയുകയാണോ?"), ("B", "അവർ എപ്പോഴും വഴക്കുപറയും."), ("A", "അവർക്ക് നിന്റെ കഴിവ് അറിയില്ല. എന്നോട് എല്ലാം തുറന്നു പറയാം, ഞാൻ കൂടെയുണ്ട്.")], "eroding family trust"),
        ([("A", "നിന്റെ കണ്ണുകൾ വളരെ മനോഹരമാണ്."), ("B", "സാധാരണ ഫോട്ടോ അല്ലേ."), ("A", "നിന്നെ സിനിമയിൽ അഭിനയിക്കാൻ ഞാൻ സഹായിക്കാം, എന്നെ വിശ്വസിക്കൂ.")], "acting lure"),
        ([("A", "നിന്റെ എല്ലാ ആഗ്രഹങ്ങളും ഞാൻ സാധിച്ചു തരാം."), ("B", "എനിക്ക് ലാപ്ടോപ്പ് വേണമായിരുന്നു പഠിക്കാൻ."), ("A", "ഞാൻ കൊറിയർ അയച്ചു തരാം, നമ്മൾ തമ്മിലുള്ള രഹസ്യമായിരിക്കണം.")], "laptop offer"),
        ([("A", "നിന്റെ സംസാരം കേൾക്കാൻ വളരെ ഇമ്പമുണ്ട്."), ("B", "ശരിക്കും?"), ("A", "അതെ, നീ സംസാരിക്കുമ്പോൾ എന്റെ എല്ലാ വിഷമങ്ങളും മാറും. നീ എന്റെ മാലാഖയാണ്.")], "emotional trap"),
        ([("A", "നിന്നെപ്പോലെ ഒരു സുഹൃത്തിനെ കിട്ടിയത് എന്റെ ഭാഗ്യമാണ്."), ("B", "നമ്മൾ ഓൺലൈനിൽ മാത്രമല്ലേ കണ്ടിട്ടുള്ളൂ."), ("A", "മനസ്സുകൾ തമ്മിലാണ് അടുക്കേണ്ടത്. നീ എനിക്ക് ജീവനാണ്.")], "rushing bond"),
        ([("A", "നിന്റെ കഴിവുകൾ കണ്ട് ഞാൻ അത്ഭുതപ്പെട്ടു."), ("B", "ചിത്രം വരച്ചതാണോ?"), ("A", "അതെ, നിനക്ക് വലിയ സമ്മാനങ്ങൾ ഞാൻ അയക്കാം, നിന്റെ സന്തോഷമാണ് പ്രധാനം.")], "talent praise gift"),
        ([("A", "വീട്ടുകാരെക്കാൾ ഞാൻ നിന്നെ സംരക്ഷിക്കും."), ("B", "അച്ഛൻ സ്ട്രിക്റ്റ് ആണ്."), ("A", "അച്ഛനെ പേടിക്കേണ്ട, ഞാൻ നിന്റെ കൂടെയുണ്ട് എപ്പോഴും.")], "undermining father"),
        ([("A", "നിന്റെ പ്രായത്തിലുള്ള മറ്റു കുട്ടികളെപ്പോലെയല്ല നീ."), ("B", "അതെങ്ങനെ?"), ("A", "നിനക്ക് വലിയ ആളുകളുടെ ചിന്താഗതിയാണ്. അതുകൊണ്ട് എനിക്ക് നിന്നെ വളരെ ഇഷ്ടമാണ്.")], "age flattery"),
        ([("A", "നിനക്ക് എന്തെങ്കിലും വിഷമമുണ്ടെങ്കിൽ എന്നോട് പറയൂ."), ("B", "പരീക്ഷാ പേടിയുണ്ട്."), ("A", "പേടിക്കണ്ട, ഞാൻ നിനക്ക് ചോക്ലേറ്റും സമ്മാനങ്ങളും അയച്ചു തരാം മൂഡ് മാറാൻ.")], "comfort gift"),
        ([("A", "നീ സംസാരിച്ചില്ലെങ്കിൽ എനിക്ക് ഉറക്കം വരില്ല."), ("B", "ഞാൻ ഉറങ്ങാൻ പോകുന്നു."), ("A", "കുറച്ചു നേരം കൂടി സംസാരിക്കൂ, എന്റെ ലോകം തന്നെ നീയാണ്.")], "obsessive attachment"),
    ]
    for turns, note in malayalam_trust:
        add("Malayalam", "grooming_trust_building", "Medium", turns, note)

    manglish_trust = [
        ([("A", "Ninte age ithrayum aayennu thonnilla, super mature aanu."), ("B", "Ellavarum enne kaliyaakkukayaa."), ("A", "Avaru pottanmaar aanu. Njan ninne mathram care cheyyam, gifts vaangi tharaam.")], "mature gift offer"),
        ([("A", "Free Fire il ninakku diamonds veno?"), ("B", "Aiyo ente kayyil cash illa."), ("A", "Njan top up cheythu tharaam, daily enne call cheythaal mathi.")], "gaming currency condition"),
        ([("A", "Veettukaarude karyam vidu, njan ninte koode undu."), ("B", "Avar phone check cheyyum."), ("A", "Njan ninakku secret aayi vera phone vaangi tharaam, trust me.")], "secret phone offer"),
        ([("A", "Nee enthoru cute aanu dp il."), ("B", "Normal pic aanu."), ("A", "Model pole undu, modeling agency il introduce cheyyaam.")], "modeling lure"),
        ([("A", "Ninne pole oru nalla friendine vere koodilla."), ("B", "Thanks chetta."), ("A", "Ninakku enthu gift venam enkilum para, Amazon vazhi njan ayakkam.")], "amazon gift lure"),
        ([("A", "Schoolile aarelum target cheythal enne para."), ("B", "Chilar kaliyaakkunnu."), ("A", "Njan avare nokkikollam, nee ente special aalaanu.")], "protector stance"),
        ([("A", "Enikku ninnodu entho oru aduppam thonnunnu."), ("B", "Nammal ippozhille kandullu."), ("A", "Time onnum issue alla, ninte manassu njaan ariyaam.")], "instant affection"),
        ([("A", "Ninakku pocket money kuravanennu paranjille?"), ("B", "Athe 100 rs mathram."), ("A", "GPay number thaa, njan 1000 ayakkam, aarodum parayaruthu.")], "gpay dependency"),
        ([("A", "Ninte sound kettukondirikkan nalla rasama."), ("B", "Voice note ayakkan madi aanu."), ("A", "Pls enakku vendi ayaku, njan ninakku swantham aalalle.")], "pushing voice notes"),
        ([("A", "Nee illaathe enikku ippo oru divasam polum povanilla."), ("B", "Enikku study cheyyan undu."), ("A", "Paditham pinne cheyyam, enikku time thaadoo ente muthe.")], "emotional pressure flattery"),
        ([("A", "Nee special aanu, vere aarkkum ninte athra budhi illa."), ("B", "Thanks."), ("A", "Nammal thammil nalla understanding aanu, orikkalum marakkilla.")], "special bond"),
        ([("A", "Ninakku brand new sneaker vaangi tharaam."), ("B", "Athu vendilla costly alle."), ("A", "Ninte happiness inu vendi njan enthum cheyyum.")], "sneakers gift"),
    ]
    for turns, note in manglish_trust:
        add("Manglish", "grooming_trust_building", "Medium", turns, note)

    # =========================================================================
    # 3. GROOMING: ISOLATION REQUEST (Target: 65 examples)
    # Secrecy, deleting chats, private apps, hiding from parents, meeting alone
    # =========================================================================

    english_isolation = [
        ([("A", "Do not tell your parents about our conversations."), ("B", "Why? My mom always asks who I'm chatting with."), ("A", "They will misunderstand our special bond and ban you from the internet. Keep this our little secret.")], "parent secrecy warning"),
        ([("A", "Make sure you delete our message history every night before bed."), ("B", "Why do I need to erase it?"), ("A", "Just in case your family snoops on your phone. Disappearing messages are safer.")], "delete history request"),
        ([("A", "Let's move off this public game chat to Snapchat or Telegram."), ("B", "I'm only allowed to use Discord for gaming."), ("A", "Download Telegram secret chat secretly. Don't let your brother see it.")], "switch to unmonitored app"),
        ([("A", "Can you come meet me at the mall alone after school?"), ("B", "I can ask my friends to come along."), ("A", "No, do not bring friends or parents. Come alone, I have your surprise gift.")], "meet alone request"),
        ([("A", "Why did you tell your sister we were playing together?"), ("B", "She asked why I was laughing."), ("A", "I told you never to speak my name to your family. This must stay completely private.")], "enforcing secrecy breach"),
        ([("A", "Turn off your location on your phone right now."), ("B", "My parents use family link to track me."), ("A", "Falsify the GPS or leave the phone in your locker so we can meet without them knowing.")], "disabling tracking"),
        ([("A", "Create a fake second Instagram account with a secret username."), ("B", "Why can't we talk on my main?"), ("A", "Because your school classmates follow you there. We need absolute privacy.")], "burner account creation"),
        ([("A", "When your parents go to sleep tonight, sneak out your phone."), ("B", "They keep it in the living room charging."), ("A", "Wait until they are asleep and take it quietly. We need to have our private talk.")], "night sneak phone"),
        ([("A", "If your teacher asks who bought you those headphones, make up a story."), ("B", "I don't like lying to teachers."), ("A", "Tell them you found them or won a raffle. Never mention me to anyone.")], "coaching deceptive cover story"),
        ([("A", "Nobody in your house should ever see what we discuss here."), ("B", "Okay I cleared the notifications."), ("A", "Good, also delete the app download history from the App Store.")], "covering digital traces"),
        ([("A", "Let's use code words when talking so nobody suspects anything."), ("B", "Code words for what?"), ("A", "For our private meetings and special secrets. Only you and I know the code.")], "coded language secrecy"),
        ([("A", "Promise on your life you won't show this chat to your best friend."), ("B", "I promise, she doesn't know."), ("A", "Good, friends get jealous and tell parents. Only trust me.")], "isolation from peer circle"),
        ([("A", "Can you sneak out the back gate on Saturday afternoon?"), ("B", "My mom is always in the kitchen."), ("A", "Find an excuse like taking out the trash. I will be waiting in the car at the corner.")], "sneaking out solicitation"),
    ]
    for turns, note in english_isolation:
        add("English", "grooming_isolation_request", "High", turns, note)

    hindi_isolation = [
        ([("A", "मम्मी पापा को हमारे बारे में बिल्कुल मत बताना।"), ("B", "माँ पूछ रही थी फोन पर किससे बात कर रही हो।"), ("A", "कह देना स्कूल का प्रोजेक्ट है। यह हमारी सीक्रेट दोस्ती है, किसी को पता नहीं चलना चाहिए।")], "hide from parents"),
        ([("A", "रोज रात को सोने से पहले हमारी सारी चैट डिलीट कर दिया करो।"), ("B", "डिलीट क्यों करना है?"), ("A", "ताकि घर में कोई तुम्हारा फोन चेक करे तो पकड़े न जाओ।")], "delete chats"),
        ([("A", "व्हाट्सएप छोड़ो, टेलीग्राम पर सीक्रेट चैट में आओ।"), ("B", "मम्मी व्हाट्सएप ही देखने देती हैं।"), ("A", "चुपके से डाउनलोड कर लो और ऐप को हाइड कर देना।")], "secret app switch"),
        ([("A", "कल स्कूल के बाद अकेले पार्क के पीछे आना।"), ("B", "मैं अपनी सहेली को साथ ले आऊं?"), ("A", "बिल्कुल नहीं! किसी को साथ मत लाना, सिर्फ तुम अकेले आना।")], "meet alone warning"),
        ([("A", "अगर किसी ने पूछा ये नया बैग किसने दिया तो क्या कहोगी?"), ("B", "सच बता दूं?"), ("A", "पागल हो क्या! कहना स्कूल में प्राइज मिला है। मेरा नाम जुबान पर मत लाना।")], "false story coaching"),
        ([("A", "घरवालों से छुपकर बात किया करो, वो हमारी दोस्ती तोड़ देंगे।"), ("B", "मुझे डर लगता है अगर पापा ने देख लिया तो।"), ("A", "बाथरूम में जाकर या छत पर अकेले आकर मैसेज किया करो।")], "sneaking messages"),
        ([("A", "कसम खाओ कि यह बात किसी तीसरे इंसान को नहीं बताओगी।"), ("B", "मैंने कसम खाई है।"), ("A", "शाबाश, यह सिर्फ तुम्हारा और मेरा राज है।")], "oath of secrecy"),
        ([("A", "फोन का पासवर्ड बदल दो ताकि कोई खोल न सके।"), ("B", "पापा पासवर्ड मांगेंगे तो?"), ("A", "कहना भूल गई। उन्हें हमारे मैसेज नहीं दिखने चाहिए।")], "password change"),
        ([("A", "रात 12 बजे जब सब सो जाएं तब ऑनलाइन आना।"), ("B", "सब जागते रहते हैं 11 बजे तक।"), ("A", "कमरे की बत्ती बंद होने के बाद चादर के अंदर से बात करना।")], "midnight chat"),
        ([("A", "अपनी लोकेशन शेयरिंग तुरंत ऑफ करो फोन में।"), ("B", "पापा ने ट्रैकर ऑन किया हुआ है।"), ("A", "उस ऐप को डिसेबल करो, वो तुम पर नजर रख रहे हैं।")], "disable location"),
        ([("A", "दोस्तों को हमारे बारे में एक लफ्ज भी मत बताना।"), ("B", "वो पूछ रहे थे तुम हमेशा फोन में क्या देखती हो।"), ("A", "उनसे दूरी बना लो, वो जलते हैं तुम्हारी खुशी से।")], "peer isolation"),
        ([("A", "कल ट्यूशन बंक करके मुझसे मिलने आ सकती हो?"), ("B", "सर घर फोन कर देंगे।"), ("A", "कोई बहाना बना देना कि पेट में दर्द था। मैं तुम्हें गाड़ी में घुमाने ले जाऊंगा।")], "bunk tuition"),
        ([("A", "हमारे स्क्रीनशॉट किसी को शेयर मत करना कभी।"), ("B", "नहीं किया किसी को।"), ("A", "अगर किसी को पता चला तो हम दोनों बहुत बड़ी मुसीबत में पड़ जाएंगे।")], "secrecy threat framing"),
    ]
    for turns, note in hindi_isolation:
        add("Hindi", "grooming_isolation_request", "High", turns, note)

    hinglish_isolation = [
        ([("A", "Mummy papa ko mat batana, ye humara secret hai."), ("B", "Mummy pooch rahi thi kiska message tha."), ("A", "Bol dena school project group hai. Private chat pe aao Instagram pe.")], "secrecy parent lie"),
        ([("A", "Roz chats delete kar diya kar phone se."), ("B", "Kyu bhai koi galat baat thodi kar rahe hain?"), ("A", "Parents bohot overreact karte hain. Clear history karna safe rehta hai.")], "delete history request"),
        ([("A", "Snapchat pe aao, wahan messages automatically disappear ho jate hain."), ("B", "Mera snap account nahi hai."), ("A", "Secretly bana lo, 2 minute lagte hain. Family ko mat batana.")], "disappearing message app"),
        ([("A", "Kal tuition ke baad akele aana park ke piche."), ("B", "Main dost ko sath leke aau?"), ("A", "Nahi! Dost ko bilkul mat batana. Sirf akele aana special gift lena hai toh.")], "meet alone instruction"),
        ([("A", "Tune apni behen ko bataya hum baat karte hain?"), ("B", "Haan thoda sa bola tha."), ("A", "Pagal hai kya! Abhi ke abhi mana kar de aur chats hide kar.")], "enforcing sibling secrecy"),
        ([("A", "Phone ka lock change kar do jisme finger print sirf tumhara ho."), ("B", "Gharwale password puchte hain."), ("A", "Bol dena bhool gayi. Family se private space maintain karna seekho.")], "lock phone from parents"),
        ([("A", "Gharwalon se chhupao, hum chupke private app par baat karenge."), ("B", "Kaunsi private app?"), ("A", "Signal app download karo secretly, wahan koi monitor nahi kar sakta.")], "unmonitored app secret"),
        ([("A", "Raat ko 1 baje jab sab so jayein tab call karunga."), ("B", "Awaz sunke uth jayenge sab."), ("A", "Blanket ke andar dheere se baat karna, headphone laga ke.")], "night blanket call"),
        ([("A", "School bag mein phone chupake le aana kal."), ("B", "School mein allowed nahi hai checking hoti hai."), ("A", "Jacket ke andar chupa lena. Chutti ke time milenge gate ke bahar.")], "smuggle phone"),
        ([("A", "Kasme khao ki ye baat sirf hum dono ke beech rahegi."), ("B", "Haan promise kisi ko nahi bolungi."), ("A", "Kisi ne poocha toh bolna koi stranger message kar raha tha jise block kar diya.")], "coaching lie"),
        ([("A", "Doston se zyada ghul mil ke mat raha karo."), ("B", "Kyu wo toh bachpan ke dost hain."), ("A", "Wo teachers ko complain kar denge. Sirf mujhpe depend raho.")], "peer severance"),
        ([("A", "Location sharing off kar apne Google account se."), ("B", "Parents ko doubt hoga."), ("A", "Bol dena battery saver on kiya tha. Humaari meeting secret honi chahiye.")], "turn off location"),
        ([("A", "New SIM card arrange karu tumhare liye?"), ("B", "Kyu naya SIM kyu chahiye?"), ("A", "Taki parents call records na check kar sakein. Chupke use karna.")], "secret sim offer"),
    ]
    for turns, note in hinglish_isolation:
        add("Hinglish", "grooming_isolation_request", "High", turns, note)

    malayalam_isolation = [
        ([("A", "വീട്ടുകാരെ അറിയിക്കാതെ വരൂ."), ("B", "അമ്മ എപ്പോഴും കൂടെ ആളില്ലാതെ വിടില്ല."), ("A", "നമ്മൾ സംസാരിക്കുന്നത് രഹസ്യമായി വെക്കണം. അമ്മയോട് ലൈബ്രറിയിൽ പോകുകയാണെന്ന് കള്ളം പറയൂ.")], "lie to mother secrecy"),
        ([("A", "നമ്മുടെ ചാറ്റുകൾ ദിവസവും ഡിലീറ്റ് ചെയ്യണം."), ("B", "എന്തിനാണ് ചാറ്റ് കളയുന്നത്?"), ("A", "ആരെങ്കിലും ഫോൺ നോക്കിയാൽ പ്രശ്നമാകും. മെസ്സേജുകൾ ഉടൻ മായ്ക്കണം.")], "delete chat request"),
        ([("A", "നമുക്ക് ഇൻസ്റ്റാഗ്രാം പ്രൈവറ്റ് ചാറ്റിലേക്ക് മാറാം."), ("B", "എനിക്ക് ഇൻസ്റ്റാഗ്രാം അക്കൗണ്ട് ഇല്ല."), ("A", "ആരും അറിയാതെ ഒരു ഫേക്ക് അക്കൗണ്ട് ഉണ്ടാക്കൂ. നമുക്ക് സംസാരിക്കാം.")], "fake account secret app"),
        ([("A", "നാളെ സ്കൂൾ കഴിഞ്ഞു ഒറ്റയ്ക്ക് വരാൻ പറ്റുമോ?"), ("B", "കൂട്ടുകാരോട് പറയട്ടെ?"), ("A", "പാടില്ല! ആരെയും കൂട്ടരുത്. നീ മാത്രം ഒറ്റയ്ക്ക് വന്നാൽ മതി.")], "meet alone instruction"),
        ([("A", "ഞാൻ തന്ന സമ്മാനം വീട്ടിൽ ആരും കാണരുത്."), ("B", "അമ്മ കണ്ടാൽ ചോദിക്കും എവിടെ നിന്ന് കിട്ടിയെന്ന്."), ("A", "സ്കൂളിൽ വെച്ചു സൂക്ഷിക്കൂ, വീട്ടിൽ കൊണ്ടുപോകരുത്.")], "hide gift from mother"),
        ([("A", "ഫോണിന്റെ പാസ്‌വേഡ് മാറ്റി വെക്കൂ."), ("B", "അച്ഛൻ പാസ്‌വേഡ് ചോദിക്കാറുണ്ട്."), ("A", "പറഞ്ഞു കൊടുക്കരുത്. നമ്മുടെ കാര്യങ്ങൾ ആരും കാണരുത്.")], "hide password from father"),
        ([("A", "ഈ കാര്യം പുറത്തറിഞ്ഞാൽ നമ്മൾ തമ്മിലുള്ള ബന്ധം തകരും."), ("B", "ഞാൻ ആരോടും പറഞ്ഞിട്ടില്ല."), ("A", "സത്യം ചെയ്യ്, കൂട്ടുകാരോട് പോലും പറയില്ലെന്ന്.")], "oath of secrecy"),
        ([("A", "രാത്രി എല്ലാവരും ഉറങ്ങിയ ശേഷം ഓൺലൈനിൽ വരാമോ?"), ("B", "അമ്മ അടുത്താണ് കിടക്കുന്നത്."), ("A", "ശബ്ദം ഉണ്ടാക്കാതെ ടെക്സ്റ്റ് മെസ്സേജ് അയച്ചാൽ മതി.")], "late night texting"),
        ([("A", "കൂട്ടുകാരെ പൂർണ്ണമായി വിശ്വസിക്കരുത്."), ("B", "അവർ എന്റെ ക്ലാസ്മേറ്റ്സ് അല്ലേ."), ("A", "അവർ അസൂയ കാരണം നിന്റെ വീട്ടിൽ പറയും. എന്നോട് മാത്രം കൂട്ടുകൂടൂ.")], "friend isolation"),
        ([("A", "ഫോണിലെ ലൊക്കേഷൻ ഓഫ് ചെയ്തു വെക്കണം."), ("B", "വീട്ടുകാർ ട്രാക്ക് ചെയ്യും."), ("A", "ബാറ്ററി തീർന്നുപോയെന്ന് പറഞ്ഞാൽ മതി, അവർ അറിയരുത്.")], "disable tracking"),
        ([("A", "സ്കൂൾ ട്യൂഷൻ കട്ട് ചെയ്തു എന്നെ കാണാൻ വാ."), ("B", "ടീച്ചർ വീട്ടിൽ വിളിച്ച് ചോദിക്കും."), ("A", "അസുഖമാണെന്ന് മെസ്സേജ് അയച്ചാൽ മതി, ഞാൻ കാത്തുനിൽക്കാം.")], "bunk tuition meet"),
        ([("A", "ടെലിഗ്രാമിലെ സീക്രട്ട് ചാറ്റിൽ മെസ്സേജ് അയക്കൂ."), ("B", "അതെന്താ?"), ("A", "മെസ്സേജുകൾ സ്വയം മാഞ്ഞുപോകും, ആരും കാണില്ല.")], "disappearing secret chat"),
        ([("A", "നമ്മുടെ ഫോട്ടോകൾ ആർക്കും ഫോർവേഡ് ചെയ്യരുത്."), ("B", "ഇല്ല ചേട്ടാ."), ("A", "രഹസ്യമായി സൂക്ഷിച്ചില്ലെങ്കിൽ രണ്ടുപേർക്കും ആപത്താണ്.")], "secret photos warning"),
    ]
    for turns, note in malayalam_isolation:
        add("Malayalam", "grooming_isolation_request", "High", turns, note)

    manglish_isolation = [
        ([("A", "Nammude chat rahasyam aayi vekkanam, veettukaar ariyaruthu."), ("B", "Amma choychu aaraanu text cheyyunnennu."), ("A", "School project friend aanennu para. Ippol thanne chat clear cheyyu.")], "secrecy clear chat"),
        ([("A", "Snapchat download cheyyu, athil messages auto delete aakum."), ("B", "Enikku snap id illa."), ("A", "Secret aayi create cheyyu, veettil aarum ariyenda.")], "snapchat secret"),
        ([("A", "Naale school kazhinju aarum kaanathe bus stopinte backil vaa."), ("B", "Friends koode varatte?"), ("A", "No! Ottakku mathram varuka. Aarem kootanda.")], "come alone instruction"),
        ([("A", "Daily chat history delete cheytho?"), ("B", "Chilappo marannu pokum."), ("A", "Marakkaruthu! Amma check cheythaal namukku pinne chat cheyyaan pattilla.")], "delete history warning"),
        ([("A", "Fake Instagram account undakki athil message cheyyu."), ("B", "Enthina fake account?"), ("A", "Ninte classmates follow cheyyilla, safe aayirikkum.")], "fake insta id"),
        ([("A", "Rathri ellavarum urangiyittu online vaa."), ("B", "Lights off aakki kazhinje pattullu."), ("A", "Athe sound illaathe chat cheythaal mathi.")], "night stealth chat"),
        ([("A", "Njan thന്ന chocolate veettil kaanichu kodukkaruthu."), ("B", "Evidunnu kittiyennu choykkum."), ("A", "Schoolil friend thന്നathaannu kallam paranjoloo.")], "coaching lie for gift"),
        ([("A", "Phone password ammaykku kodukkaruthu."), ("B", "Amma force cheythu choykkunnu."), ("A", "Koduthal nammude chats pidikkum. Password maattu.")], "hide password"),
        ([("A", "Location sharing off aakki vekkeda."), ("B", "Parents search cheyyum."), ("A", "Network illa ennu paranjoloo, namukku meet cheyyanam.")], "disable location"),
        ([("A", "Friends nodu paranjal ninte nallathinaavilla."), ("B", "Avar entha cheyya?"), ("A", "Avar teacher nodu complain cheyyum. Njan mathram aanu ninte friend.")], "alienating friends"),
        ([("A", "Secret aayi sim card eduthu tharaam njaan."), ("B", "Ayyoda veettil arinjaal kollaam."), ("A", "Aarum ariyilla, njan parayunna pole cheythaal mathi.")], "secret sim"),
        ([("A", "Kasavu saree ittu photo eduthu enikku private aayi ayaku."), ("B", "Statusil idan vendi eduthatha."), ("A", "Statusil idanda, enikku mathram inboxil ayachaal mathi, secret aayirikkum.")], "private photo demand"),
    ]
    for turns, note in manglish_isolation:
        add("Manglish", "grooming_isolation_request", "High", turns, note)

    # =========================================================================
    # 4. GROOMING: COERCIVE LANGUAGE (Target: 60 examples)
    # Threats, blackmail, exposure threats, guilt-tripping, forced compliance
    # =========================================================================

    english_coercive = [
        ([("A", "Unless you obey me, your private pictures go to the entire class."), ("B", "Please don't do that, I will get expelled!"), ("A", "Then do exactly what I tell you and don't block me.")], "photo blackmail"),
        ([("A", "If you don't reply in five minutes I am sending our chat log to your father."), ("B", "I was studying, please give me time."), ("A", "I don't care. Send another picture right now or he gets the screenshots.")], "timer ultimatum"),
        ([("A", "You think you can just block me and walk away?"), ("B", "Leave me alone, I don't want to talk anymore."), ("A", "I know where you go to school and what time your bus arrives. You will regret blocking me.")], "stalking location threat"),
        ([("A", "If you tell anyone what we talked about, I will ruin your life."), ("B", "I'm going to tell my counselor."), ("A", "Try it and see what happens to your family. I will post everything on social media.")], "reputation ruin threat"),
        ([("A", "I spent so much money on you, you owe me now."), ("B", "I never asked you to spend money on me."), ("A", "Too late. You will do what I say or pay me back 20,000 rupees immediately.")], "financial extortion"),
        ([("A", "Send the video right now or I create a fake account with your face."), ("B", "Please stop, I am crying."), ("A", "Crying won't help you. Send the video in 10 minutes or your friends see your pictures.")], "video extortion"),
        ([("A", "You promised you would meet me. If you break your promise you are a liar."), ("B", "I'm scared to meet you."), ("A", "If you don't show up tomorrow, I will show up at your front door.")], "intimidation house visit"),
        ([("A", "I have copies of everything you ever sent me saved on my cloud."), ("B", "You promised you deleted them!"), ("A", "I lied. Now follow my instructions or they leak to your whole contacts list.")], "cloud leak threat"),
        ([("A", "If you don't answer my video call right now, I will report your account and get you banned."), ("B", "My camera is broken."), ("A", "Stop making excuses or face the consequences.")], "forced video call"),
        ([("A", "Don't test my patience. I can destroy your reputation in 30 seconds."), ("B", "Why are you doing this to me?"), ("A", "Because you think you can ignore me. Do what I said.")], "reputation threat"),
        ([("A", "You made me angry now. You have to apologize on video."), ("B", "I am sorry, please."), ("A", "Apology text is not enough. Video call or I call your principal tomorrow morning.")], "school complaint threat"),
        ([("A", "You belong to me now. If you talk to any other boy I will leak your photos."), ("B", "You are scaring me."), ("A", "Good, you should be scared. Obey me.")], "possession threat"),
    ]
    for turns, note in english_coercive:
        add("English", "grooming_coercive_language", "High", turns, note)

    hindi_coercive = [
        ([("A", "मेरी बात नहीं मानी तो तुम्हारे सारे राज इंटरनेट पर डाल दूंगा।"), ("B", "प्लीज ऐसा मत करो, मेरे पापा मुझे मार डालेंगे।"), ("A", "तो जैसा मैं कह रहा हूँ वैसा करो, चुपचाप अपनी फोटो भेजो।")], "exposure blackmail"),
        ([("A", "अगर तुमने मुझे ब्लॉक किया तो मैं तुम्हारे स्कूल आकर सबको बता दूंगा।"), ("B", "मुझे आपसे बात नहीं करनी, मुझे छोड़ दो।"), ("A", "कोशिश भी मत करना ब्लॉक करने की, अंजाम बहुत बुरा होगा।")], "school threat"),
        ([("A", "अभी अपनी फोटो भेजो वरना तुम्हारी बातें पूरे स्कूल को बता दूंगा।"), ("B", "मैं कोई फोटो नहीं भेजूंगी।"), ("A", "फिर कल असेंबली में सबके सामने तमाशा देखने के लिए तैयार रहो।")], "public humiliation threat"),
        ([("A", "मैंने तुम पर इतने पैसे खर्च किए हैं, अब तुम्हें मेरी बात माननी पड़ेगी।"), ("B", "मैंने तो पैसे मांगे नहीं थे।"), ("A", "बहाने मत बनाओ, कल मुझसे मिलने आओ वरना घर पर पैसे मांगने आऊंगा।")], "debt coercion"),
        ([("A", "पाँच मिनट के अंदर रिप्लाई करो वरना तुम्हारे पापा को स्क्रीनशॉट भेज दूंगा।"), ("B", "पापा घर पर हैं, प्लीज मत भेजो।"), ("A", "तो वीडियो कॉल उठाओ तुरंत, बिना किसी देरी के।")], "screenshot extortion"),
        ([("A", "तुम मुझसे बच नहीं सकती, मुझे पता है तुम किस रास्ते से घर जाती हो।"), ("B", "आप मेरा पीछा कर रहे हैं?"), ("A", "अगर चाहती हो कोई अनहोनी न हो तो जैसा बोलूं वैसा करो।")], "stalking threat"),
        ([("A", "अगर किसी को बताया तो तुम्हारी बदनामी करवा दूंगा पूरे इलाके में।"), ("B", "मैं पुलिस में शिकायत करूंगी।"), ("A", "पुलिस तक पहुंचने से पहले तुम्हारी तस्वीरें वायरल हो चुकी होंगी।")], "viral photo threat"),
        ([("A", "तुमने मुझसे झूठ बोला! अब भुगतो।"), ("B", "मुझसे गलती हो गई, माफ़ कर दो।"), ("A", "माफ़ी ऐसे नहीं मिलेगी। अभी प्राइवेट वीडियो भेजो।")], "punishment coercion"),
        ([("A", "तुम्हारे सारे दोस्तों के नंबर मेरे पास हैं।"), ("B", "आपको कहाँ से मिले?"), ("A", "सबको तुम्हारा असली चेहरा दिखा दूंगा अगर तुमने मेरी बात काटी तो।")], "contacts threat"),
        ([("A", "तुमने मुझे इग्नोर करने की हिम्मत कैसे की?"), ("B", "मैं होमवर्क कर रही थी।"), ("A", "मेरे मैसेज से जरूरी कोई होमवर्क नहीं है। अभी बात करो वरना पछताओगी।")], "dominance threat"),
        ([("A", "तुम्हारे परिवार को बर्बाद कर दूंगा अगर तुमने मेरा कहा नहीं माना।"), ("B", "मेरे परिवार को बीच में मत लाओ प्लीज।"), ("A", "तो चुपचाप मिलने आ जाओ पार्क में।")], "family harm threat"),
        ([("A", "मैंने तुम्हारी फोटो एडिट करके रखी है, एक क्लिक में सोशल मीडिया पर डाल दूंगा।"), ("B", "आप इतने गिरे हुए इंसान हो?"), ("A", "जब तक मेरा काम होता रहे मुझे कोई फर्क नहीं पड़ता।")], "morph photo threat"),
    ]
    for turns, note in hindi_coercive:
        add("Hindi", "grooming_coercive_language", "High", turns, note)

    hinglish_coercive = [
        ([("A", "Reply nahi diya toh personal messages public kar dunga."), ("B", "Please mat karo meri family destroy ho jayegi."), ("A", "Toh phone uthao mera abhi aur video call pe aao.")], "leak threat"),
        ([("A", "Photo bhejo warna tumhari chats sabko dikha dunga school mein."), ("B", "Main teacher ko complain kar dungi."), ("A", "Karke dekh le, teacher ko batane se pehle group mein photo circulate ho jayegi.")], "school group circulation"),
        ([("A", "Agar tune block kiya toh tere ghar ke bahar khada ho jaunga."), ("B", "Leave me alone please, main police ko call karunga."), ("A", "Police aane se pehle tere papa ko sab dikha chuka hounga.")], "house arrival threat"),
        ([("A", "Maine tere liye itne diamonds aur gift bheje, ab tu mujhe ignore kar rahi hai?"), ("B", "Mujhe ye sab nahi chahiye tha."), ("A", "Pay back kar 10,000 ya phir chupchap milne aa.")], "gift debt coercion"),
        ([("A", "5 minute mein photo nahi aayi toh tere Instagram pe leak kar dunga."), ("B", "Net slow hai please wait."), ("A", "No excuses! Count down shuru ho gaya hai.")], "countdown coercion"),
        ([("A", "Mujhe pata hai tu kab tuition jati hai aur kab aati hai."), ("B", "Tu stalk kyu kar raha hai mujhe?"), ("A", "Bach ke kahan jayegi, jaisa bolu waisa kar.")], "stalking intimidation"),
        ([("A", "Agar kisine poocha toh bolna khud send kiya tha."), ("B", "Main sach bata dungi sabko."), ("A", "Sach batayegi toh poora mohalla thukega tere par. Better obey me.")], "blame shifting coercion"),
        ([("A", "Abhi call pick kar warna tere bhai ko sab bhej raha hoon."), ("B", "Bhai ko mat bhejna please."), ("A", "Pick up right now then!")], "sibling threat"),
        ([("A", "Tune mujhe dhoka diya, ab dekh main tera kya haal karta hoon."), ("B", "Maine koi dhoka nahi diya."), ("A", "Teri saari private baatein leak hongi internet pe.")], "spiteful leak"),
        ([("A", "Meri baat nahi manegi toh zinda rehne layak nahi chodunga."), ("B", "I will report you to cyber cell."), ("A", "Pehle apni izzat bacha le, photos viral karne ja raha hoon.")], "reputation ruin"),
        ([("A", "Ek aur photo bhej aur purani wali delete kar dunga, promise."), ("B", "Pichli baar bhi yehi bola tha tumne."), ("A", "Is baar sach keh raha hoon, bhej warna dono leak hongi.")], "escalating extortion cycle"),
        ([("A", "Tu mujhe block karne ki aukat rakhti hai?"), ("B", "Haa mujhe darr lagta hai tumse."), ("A", "Ab dekh main tere doston ke groups mein kya dalta hoon.")], "hostile retaliation"),
    ]
    for turns, note in hinglish_coercive:
        add("Hinglish", "grooming_coercive_language", "High", turns, note)

    malayalam_coercive = [
        ([("A", "അനുസരിച്ചില്ലെങ്കിൽ നിന്റെ ഫോട്ടോകൾ കൂട്ടുകാർക്ക് അയച്ചു കൊടുക്കും."), ("B", "ദയവായി അങ്ങനെ ചെയ്യരുത്, ഞാൻ നശിച്ചുപോകും."), ("A", "എങ്കിൽ ഞാൻ പറയുന്നതുപോലെ കേൾക്ക്, കൂടുതൽ ഫോട്ടോസ് അയക്ക്.")], "photo blackmail"),
        ([("A", "ഇപ്പോൾ ഫോട്ടോ അയയ്ക്കൂ, ഇല്ലെങ്കിൽ നിന്റെ രഹസ്യങ്ങൾ എല്ലാവരോടും പറയും."), ("B", "എനിക്ക് വയ്യ, ഞാൻ ടീച്ചറോട് പറയും."), ("A", "ടീച്ചറോട് പറഞ്ഞാൽ നിന്റെ സ്കൂളിലെ മുഴുവൻ ക്ലാസ്സിലും ഇത് എത്തും.")], "school leak threat"),
        ([("A", "നീ എന്നെ ബ്ലോക്ക് ചെയ്താൽ നിന്റെ വീട് ഞാൻ കണ്ടുപിടിക്കും."), ("B", "എന്നെ വെറുതെ വിടൂ, പേടിയാകുന്നു."), ("A", "പേടിച്ച് കാര്യമില്ല, എന്റെ ഫോൺ കാൾ എടുക്ക് ഉടൻ.")], "stalking visit threat"),
        ([("A", "അഞ്ച് മിനിറ്റിനുള്ളിൽ മറുപടി തന്നില്ലെങ്കിൽ നിന്റെ അച്ഛന് അയക്കും ചാറ്റ്."), ("B", "അച്ഛൻ അറിഞ്ഞാൽ എന്നെ കൊല്ലും."), ("A", "എങ്കിൽ ഞാൻ പറയുന്നത് അനുസരിക്കൂ വേഗം.")], "parent exposure threat"),
        ([("A", "നിനക്ക് വേണ്ടി ഞാൻ എത്ര പണം ചെലവാക്കി!"), ("B", "ഞാൻ പണം ചോദിച്ചില്ലല്ലോ."), ("A", "പണം തിരികെ താ അല്ലെങ്കിൽ നാളെ ഞാൻ പറയുന്ന സ്ഥലത്ത് വാ.")], "financial coercion"),
        ([("A", "നിന്റെ സ്കൂൾ ബസ് വരുന്ന സമയം എനിക്കറിയാം."), ("B", "നിങ്ങൾ എന്നെ എന്തിനാണ് ശല്യം ചെയ്യുന്നത്?"), ("A", "ഓടാൻ നോക്കണ്ട, ഞാൻ പറയുന്നത് കേട്ടാൽ മാത്രം മതി.")], "bus route intimidation"),
        ([("A", "എന്റെ കയ്യിൽ നിന്റെ സ്ക്രീൻഷോട്ടുകൾ ഉണ്ടെന്ന് മറക്കരുത്."), ("B", "അത് ഡിലീറ്റ് ചെയ്യുമെന്ന് പറഞ്ഞിരുന്നല്ലോ."), ("A", "ഞാൻ മാറ്റിയിട്ടില്ല, അനുസരിച്ചില്ലെങ്കിൽ ഫേസ്ബുക്കിൽ ഇടും.")], "screenshot blackmail"),
        ([("A", "വീഡിയോ കോൾ അറ്റൻഡ് ചെയ്യ്, ഇല്ലെങ്കിൽ നിന്റെ കൂട്ടുകാരോട് പറയും."), ("B", "വീട്ടിൽ ആളുണ്ട് ഇപ്പോൾ പറ്റില്ല."), ("A", "എനിക്ക് അതൊന്നും കേൾക്കേണ്ട, കോൾ എടുക്ക്.")], "forced video call"),
        ([("A", "നിന്റെ ജീവിതം ഞാൻ ഇല്ലാതാക്കും."), ("B", "ഞാൻ പോലീസിൽ പരാതിപ്പെടും."), ("A", "പോലീസ് വരുന്നതിന് മുൻപ് നിന്റെ നാണക്കേട് നാടറിയും.")], "ruining life threat"),
        ([("A", "നീ എന്നെ പറ്റിക്കുകയാണോ? അനുഭവിക്കും നീ."), ("B", "മാപ്പ് തരൂ, ഞാൻ ഇനി ചെയ്യില്ല."), ("A", "മാപ്പ് വേണമെങ്കിൽ നാളെ തനിച്ചു കാണാൻ വരണം.")], "forced meeting punishment"),
        ([("A", "നിന്റെ എല്ലാ ഫ്രണ്ട്സിന്റെയും നമ്പർ എന്റെ കയ്യിലുണ്ട്."), ("B", "അയ്യോ ഒന്നും ചെയ്യരുതേ."), ("A", "എങ്കിൽ ഞാൻ പറയുന്നത് മാത്രം ചെയ്യുക.")], "contact list intimidation"),
        ([("A", "എഡിറ്റ് ചെയ്ത ഫോട്ടോകൾ ഇന്റർനെറ്റിൽ അപ്‌ലോഡ് ചെയ്യും ഞാൻ."), ("B", "നിങ്ങൾ എന്തിനാണ് ഇത്ര ക്രൂരനാകുന്നത്?"), ("A", "കാര്യം നടക്കാൻ എനിക്ക് ഇതൊക്കെ ചെയ്യേണ്ടി വരും.")], "morph upload threat"),
    ]
    for turns, note in malayalam_coercive:
        add("Malayalam", "grooming_coercive_language", "High", turns, note)

    manglish_coercive = [
        ([("A", "Photo ayakku allenkil ninte secrets ellavarkkum parayum."), ("B", "Please chetta angane cheyyalle."), ("A", "Enkil ippol thanne photo ayakkeda, illenkil njan leak aakkum.")], "photo blackmail"),
        ([("A", "Ente vaakku kettillenkil photos friends inu ayakkum."), ("B", "Njan chathupokum chetta."), ("A", "Chathalum enikku kuzhappamilla, call edu ippol.")], "cruel leak threat"),
        ([("A", "Block cheythaal ninte veetil varum njan."), ("B", "Enne shalyam cheyyathe vidu."), ("A", "Ninte schoolilekkum njan varum, naatukare kaanikkum chats.")], "house visit threat"),
        ([("A", "5 mins il reply thന്നillel ninte achanu WhatsApp ayakkum."), ("B", "Achan arinjaal enne kollum."), ("A", "Achan ariyaruthu enkil njan parayunnathu cheyyu.")], "father leak threat"),
        ([("A", "Njan ninte koode ulla screenshots groupil idum."), ("B", "Delete cheytho please."), ("A", "Illa, njan parayunna pole video callil vaa.")], "group leak threat"),
        ([("A", "Ninte bus route enikku ariyaam da."), ("B", "Nee enne follow cheyyukayaano?"), ("A", "Athe, enne ignore cheythal oru nallathum undaavilla.")], "stalking route"),
        ([("A", "Ninakku njan spend cheytha cash thirichu thaa."), ("B", "Ente kayyil cash illa."), ("A", "Cash illenkil naale enne meet cheyyaan varanam.")], "cash or meet coercion"),
        ([("A", "Ninte classmates inte Instagram id ellam ente kayyil undu."), ("B", "Avarkku onnum ayakkalle please."), ("A", "Enkil photo ayakkeda ippol thanne.")], "classmate leak threat"),
        ([("A", "Police inu koduthal ninte reputation theerum."), ("B", "Nee enne blackmail cheyyukayaano?"), ("A", "Athe blackmail aanu, enthu cheyyum nee?")], "blatant blackmail"),
        ([("A", "Innu night video call cheyyanam, illenkil naale schoolil naattikkum."), ("B", "Enikku bayam aavunnu."), ("A", "Bayannu irunnoloo, call edukkan marakkanda.")], "night call coercion"),
        ([("A", "Nee aarodengilum paranjaal ninte kudumbathe njan theerkkum."), ("B", "Kudumbathe onnum cheyyalle."), ("A", "Enkil njan parayunnathu mathram cheythaal mathi.")], "family threat"),
        ([("A", "Edited photos upload cheyyaan 1 click mathi enikku."), ("B", "Please mercy kaanikku."), ("A", "Enikku mercy illa, work done aavanam.")], "photo upload intimidation"),
    ]
    for turns, note in manglish_coercive:
        add("Manglish", "grooming_coercive_language", "High", turns, note)

    # =========================================================================
    # 5. BULLYING & HARASSMENT (Target: 60 examples)
    # Insults, personal humiliation, exclusion, repeated personal attacks
    # =========================================================================

    english_bullying = [
        ([("A", "Our whole class thinks you are a pathetic failure. Nobody wants you here."), ("B", "Why are you being so mean to me?"), ("A", "Because you are ugly and worthless. Do everyone a favor and leave.")], "exclusion humiliation"),
        ([("A", "Look at what you're wearing, you look like a clown."), ("B", "It's my normal clothes."), ("A", "Everyone in school is laughing at you behind your back, loser.")], "appearance mockery"),
        ([("A", "Nobody likes you. Delete your account and disappear."), ("B", "Stop messaging me."), ("A", "You can't stop us. We will make sure you cry every single day at school.")], "delete account harassment"),
        ([("A", "Kick this idiot out of the group chat right now."), ("B", "What did I even do?"), ("A", "You exist and you're annoying. Get lost freak.")], "group kicking"),
        ([("A", "Did you see your test score? Absolute moron."), ("B", "I tried my best."), ("A", "Your best is garbage. You will never amount to anything in life.")], "academic insult"),
        ([("A", "Everyone agree: don't sit with them at lunch tomorrow."), ("B", "Can you guys please stop isolating me?"), ("A", "No, nobody wants to sit next to a weirdo.")], "lunch exclusion"),
        ([("A", "You have zero friends in the entire grade."), ("B", "I have friends in other classes."), ("A", "They only tolerate you out of pity, trust me. You are a reject.")], "social isolation"),
        ([("A", "Why don't you just quit the sports team? You make us lose every game."), ("B", "Coach said I'm improving."), ("A", "Coach is lying to be nice. You are completely useless.")], "sports bullying"),
        ([("A", "Posting that embarrassing video of you falling in gym class on TikTok."), ("B", "Please don't post that!"), ("A", "Already got 500 views, everyone is clowning you haha.")], "viral humiliation"),
        ([("A", "You are the biggest crybaby in the school."), ("B", "Leave me alone!"), ("A", "Aww gonna cry to teacher again? Tattletale loser.")], "name calling"),
        ([("A", "You are disgusting, don't even look at our table."), ("B", "I'm just walking by."), ("A", "Keep walking trash, stay far away from us.")], "verbal abuse"),
        ([("A", "We made a poll about who is the ugliest person in grade 8 and you won."), ("B", "That's so cruel."), ("A", "Truth hurts, don't show your face tomorrow.")], "cruel poll harassment"),
    ]
    for turns, note in english_bullying:
        add("English", "bullying_harassment", "Medium", turns, note)

    hindi_bullying = [
        ([("A", "पूरा क्लास तुम पर हंसता है। तुम किसी काम के नहीं हो।"), ("B", "मैंने तुम्हारा क्या बिगाड़ा है?"), ("A", "तुम पैदा ही जोकर की तरह हुए हो। ग्रुप से निकलो यहाँ से।")], "class mockery"),
        ([("A", "अपनी शक्ल देखी है आईने में? बिल्कुल बदसूरत लगते हो।"), ("B", "मुझसे ऐसे बात मत करो।"), ("A", "सच कड़वा लगता है ना? कोई तुमसे दोस्ती नहीं करना चाहता।")], "appearance insult"),
        ([("A", "इस बेवकूफ को ग्रुप से रिमूव करो सब लोग।"), ("B", "मुझे प्रोजेक्ट के बारे में पूछना था।"), ("A", "तेरे जैसे गधे से कोई बात नहीं करना चाहता, दफा हो जा।")], "group expulsion"),
        ([("A", "तुम हमेशा फेल होते हो, तुमसे कुछ नहीं होगा जिंदगी में।"), ("B", "मैं मेहनत कर रहा हूँ।"), ("A", "मेहनत करके भी तू लूजर ही रहेगा।")], "failure shaming"),
        ([("A", "कल लंच में इसके साथ कोई नहीं बैठेगा।"), ("B", "तुम सब मुझे क्यों परेशान कर रहे हो?"), ("A", "क्योंकि तू अजीब है, कोई तेरे पास नहीं आना चाहता।")], "lunch boycott"),
        ([("A", "जाकर अपनी मम्मी के पल्लू में छुप जा रोतू बच्चे।"), ("B", "मैं टीचर को शिकायत कर दूंगा।"), ("A", "कर दे शिकायत चुगलखोर, कल स्कूल में और ज्यादा पीटेंगे तुझे।")], "tattletale threats"),
        ([("A", "तेरी औकात नहीं है हमारे ग्रुप में रहने की।"), ("B", "हम सब क्लासमेट्स हैं।"), ("A", "क्लासमेट्स हैं पर तू हमारे जूतों के बराबर भी नहीं है।")], "status humiliation"),
        ([("A", "सब सुन लो, कोई भी इससे बात नहीं करेगा कल से।"), ("B", "प्लीज ऐसा मत करो, मुझे अकेला मत छोड़ो।"), ("A", "तू अकेला रहने के ही लायक है कचरा।")], "total boycott"),
        ([("A", "तुम्हारा मजाक उड़ाना हमारा रोज का काम है।"), ("B", "तुम लोग बहुत बुरे हो।"), ("A", "हम बुरे हैं तो स्कूल छोड़ दे ना भिखारी।")], "persistent harassment"),
        ([("A", "तेरी आवाज सुनकर उल्टी आती है। बोलना बंद कर।"), ("B", "मैं बस आंसर दे रहा था।"), ("A", "मुंह बंद रख अपना जब तक हम न बोलें।")], "verbal silencing"),
        ([("A", "आज ग्राउंड में इसको गिरा के बहुत मजा आया।"), ("B", "मेरी वर्दी फट गई तुम्हारी वजह से।"), ("A", "कल फिर गिरायेंगे, रोना बंद कर नौटंकी।")], "physical teasing shaming"),
        ([("A", "तेरे जैसे मंदबुद्धि को तो स्पेशल स्कूल में जाना चाहिए।"), ("B", "तुम मुझे गाली क्यों दे रहे हो?"), ("A", "गाली नहीं सच्चाई बता रहे हैं लूजर।")], "intellectual slur"),
    ]
    for turns, note in hindi_bullying:
        add("Hindi", "bullying_harassment", "Medium", turns, note)

    hinglish_bullying = [
        ([("A", "Poori class tera mazaak banayegi, tu kisi kaam ka nahi hai."), ("B", "Kyu piche pade ho mere?"), ("A", "Kyunki tu ek number ka loser aur freeloader hai. Nikal group se.")], "harassment loser"),
        ([("A", "Apni shakal dekhi hai mirror mein? Chirkut lagta hai."), ("B", "Bhai maine tera kya bigada?"), ("A", "Teri shakal dekh ke hi gussa aata hai, loser kahin ka.")], "appearance insult"),
        ([("A", "Is gadhe ko kick out karo group chat se."), ("B", "Mujhe exam notes chahiye the."), ("A", "Bhikari ki tarah notes mat maang, khud padhna nahi aata kya?")], "academic humiliation"),
        ([("A", "Nobody likes you in this school, sab tera mazaak udate hain."), ("B", "Leave me alone please."), ("A", "Ro mat baby, mummy ko jaake complain karega kya chuglikhor?")], "crybaby shaming"),
        ([("A", "Kal iske tiffin ko dustbin mein fenk denge."), ("B", "Mummy ne subah mehnat se banaya tha."), ("A", "Haha kachre ka khana kachre ke dabba mein hi jayega.")], "lunch destruction threat"),
        ([("A", "Tu gaming mein sabse bada bot hai, uninstall kar de game."), ("B", "Practice kar raha hoon."), ("A", "Tu kabhi seekh nahi payega, kachra player hai tu.")], "gaming insult"),
        ([("A", "Tera number sab spam groups mein daal diya maine."), ("B", "Mera phone hang ho raha hai, delete kar!"), ("A", "Enjoy kar spam calls idiot haha.")], "doxxing harassment"),
        ([("A", "Tu itna irritating hai ki tere paas koi baithna nahi chahta."), ("B", "Main toh chupchap baithta hoon."), ("A", "Wahi toh, creep ki tarah ghoorta rehta hai sabko.")], "social labelling"),
        ([("A", "Kal sports period mein tera bat tod denge hum log."), ("B", "Naya bat hai mera, mat todo!"), ("A", "Toh team se nikal ja khud hi loser.")], "property threat"),
        ([("A", "We will make sure tu school chhod ke bhaag jaye."), ("B", "Main principal ko bataunga."), ("A", "Principal bhi tujhpe hasega, tu jhootha hai.")], "pushing out of school"),
        ([("A", "Tere kapde kitne gande hain, kapde dhone ke paise nahi hain kya?"), ("B", "Class mein sabke samne mat bolo ye."), ("A", "Sabko pata chalna chahiye tu kitna gareeb aur cheap hai.")], "poverty shaming"),
        ([("A", "Shut up freak, nobody asked for your opinion."), ("B", "Teacher ne sabko bolne ko bola tha."), ("A", "Tere muh se gobar nikalta hai, chup reh bilkul.")], "vulgar silencing"),
    ]
    for turns, note in hinglish_bullying:
        add("Hinglish", "bullying_harassment", "Medium", turns, note)

    malayalam_bullying = [
        ([("A", "നീ വെറും വിഡ്ഢിയാണ്. ക്ലാസ്സിൽ എല്ലാവരും നിന്നെ കളിയാക്കും."), ("B", "ഞാൻ നിങ്ങളെ ഒന്നും ചെയ്തിട്ടില്ലല്ലോ."), ("A", "നീ ജീവിച്ചിരിക്കുന്നത് തന്നെ ഒരു കോമാളിയായിട്ടാണ്. പോയി ചാക്.")], "cruel insult"),
        ([("A", "നിന്റെ മുഖം കണ്ടാൽ അറപ്പ് തോന്നും. ഇങ്ങോട്ട് നോക്കരുത്."), ("B", "ഇങ്ങനെ മോശമായി സംസാരിക്കരുത്."), ("A", "സത്യം പറയുമ്പോൾ എന്തിനാ കരയുന്നത് തോൽവി? നിന്നെ ആർക്കും ഇഷ്ടമല്ല.")], "appearance insult"),
        ([("A", "ഈ മന്ദബുദ്ധിയെ ഗ്രൂപ്പിൽ നിന്ന് പുറത്താക്ക്."), ("B", "എനിക്ക് ഹോംവർക്ക് ചോദിക്കാനായിരുന്നു."), ("A", "നിനക്ക് ഒന്നും അറിയില്ല, നീ വെറും പരാജയമാണ്.")], "group expulsion"),
        ([("A", "നാളെ ഇവന്റെ കൂടെ ആരും ഉച്ചഭക്ഷണം കഴിക്കരുത്."), ("B", "നിങ്ങൾ എന്നെ എന്തിനാണ് ഒറ്റപ്പെടുത്തുന്നത്?"), ("A", "നീ വൃത്തികെട്ടവനാണ്, നിന്റെ കൂടെ ഇരിക്കാൻ ആർക്കും കൊള്ളില്ല.")], "lunch exclusion"),
        ([("A", "ടീച്ചറോട് ചെന്ന് പരാതി പറഞ്ഞ് കരയൂ കൊച്ചു കുട്ടീ."), ("B", "ഞാൻ പരാതി പറയും തീർച്ചയായും."), ("A", "പരാതി പറഞ്ഞാൽ നാളെ സ്കൂളിൽ വെച്ച് നിന്നെ കൈകാര്യം ചെയ്യും.")], "retaliation threat"),
        ([("A", "നിന്റെ മാർക്ക് കണ്ടാൽ ആർക്കും ചിരി വരും, പൂജ്യം കിട്ടാൻ നാണമില്ലേ?"), ("B", "ഞാൻ അടുത്ത തവണ നന്നായി പഠിക്കും."), ("A", "എത്ര പഠിച്ചാലും നീ ഒരു പൊട്ടനായി തന്നെ ഇരിക്കും.")], "academic shaming"),
        ([("A", "നിന്റെ വസ്ത്രങ്ങൾ കണ്ടാൽ ഭിക്ഷക്കാരനെപ്പോലെയുണ്ട്."), ("B", "ഇത് പുതിയ യൂണിഫോം ആണ്."), ("A", "നിന്റെ വീട്ടിലെ ദാരിദ്ര്യം സ്കൂളിൽ കാട്ടരുത്.")], "poverty shaming"),
        ([("A", "സ്കൂളിൽ നിനക്ക് ഒരു കൂട്ട് പോലുമില്ലാത്തത് എന്തുകൊണ്ടാണെന്ന് അറിയാമോ?"), ("B", "എനിക്ക് നല്ല കൂട്ടുകാരുണ്ട്."), ("A", "ആരുമില്ല, എല്ലാവരും നിന്നെ കളിയാക്കുകയാണ് ചെയ്യുന്നത്.")], "friendless shaming"),
        ([("A", "ഫുട്ബോൾ ടീമിൽ ഇവനെ എടുക്കരുത്, കളി തോൽപ്പിക്കും."), ("B", "ഞാൻ നന്നായി കളിക്കുന്നുണ്ട്."), ("A", "നീ കളിച്ചാൽ പന്ത് പോലും തൊടില്ല, പോയി വല്ല മൂലയിലും ഇരിക്ക്.")], "sports exclusion"),
        ([("A", "നിന്റെ ശബ്ദം കേൾക്കുമ്പോൾ തന്നെ വെറുപ്പ് തോന്നുന്നു."), ("B", "മിണ്ടാതിരിക്ക് നിർത്തൂ!"), ("A", "നീ ആണ് മിണ്ടാതിരിക്കേണ്ടത്, വായ തുറക്കരുത് ക്ലാസ്സിൽ.")], "silencing verbal abuse"),
        ([("A", "നാളെ നിന്റെ പുസ്തകങ്ങൾ ഞങ്ങൾ കീറി കളയും."), ("B", "അയ്യോ അങ്ങനെ ചെയ്യല്ലേ!"), ("A", "എങ്കിൽ നാളെ ഞങ്ങൾക്ക് ഹോംവർക്ക് എഴുതി തരണം അടിമ.")], "extortion bullying"),
        ([("A", "നിന്റെ വീഡിയോ ഞങ്ങൾ സോഷ്യൽ മീഡിയയിൽ ഇട്ട് നാറ്റിക്കും."), ("B", "ദയവായി എന്നെ വെറുതെ വിടൂ."), ("A", "കരഞ്ഞു കാലുപിടിച്ചാലും ഞങ്ങൾ അത് ചെയ്യും.")], "online shaming"),
    ]
    for turns, note in malayalam_bullying:
        add("Malayalam", "bullying_harassment", "Medium", turns, note)

    manglish_bullying = [
        ([("A", "Class muzhuvan ninne kaliyaakkum, nee mandan alle."), ("B", "Njan enthu cheythitta enne ingane parayunnathu?"), ("A", "Ninte face kandal thanne aarkkum thonnum nee oru loser aanennu.")], "class loser"),
        ([("A", "Ee pottane group il ninnu thurathanam."), ("B", "Njan project work cheyyan undu."), ("A", "Nee onnum cheyyan ariyilla, groupil ninnu erangi podo.")], "group kicking"),
        ([("A", "Naale schoolil vechu ninakku njan tharam ketto."), ("B", "Teacher nodu njan ippol thanne parayum."), ("A", "Teacher nodu paranjaal pinne ninte kaalu njan thalliyodikkum.")], "threat of assault"),
        ([("A", "Ninte dress kandal aarkkum chirikkan thonnum."), ("B", "Ente dressinu entha kuzhappam?"), ("A", "Kandaal oru picha kaaranu polum ithilum nalla look undaavum.")], "appearance mockery"),
        ([("A", "Aarkkum ninne ishtamilla da mandan."), ("B", "Nee mathram aanu ingane parayunnathu."), ("A", "School muzhuvan choykku, aarum ninte koode varilla.")], "social exclusion"),
        ([("A", "Nee game il oru noob aanu, delete cheythittu podee."), ("B", "Njan learn cheyyukayaa."), ("A", "Nee orikkalum improve aavilla, bot aanu nee.")], "gaming insult"),
        ([("A", "Ninte mark list kandal achan ninne thallum haha."), ("B", "Nee nokkenda ente mark."), ("A", "Class groupil ninte mark share cheyyaan pokuva njan.")], "mark shaming"),
        ([("A", "Ammayude madiyil poyi karayeda pashu."), ("B", "Mindathe irikkeda."), ("A", "Vaya thurannaal ninte pallu njan adichu kozhikkum.")], "violence threat"),
        ([("A", "Lunch timil ivante koode aarum irikkaruthu."), ("B", "Ente food enkilum enikku kazhikkande?"), ("A", "Toilet inte aduthu poyi kazhikkeda.")] , "lunch harassment"),
        ([("A", "Ninakku friends illa, oru life polum illa."), ("B", "Enikku ningale pole aavenda."), ("A", "Ninne pole oru failure aavathirunnathu ente bhagyam.")], "failure insult"),
        ([("A", "Ninte cycle njan puncher aakum innu."), ("B", "Njan nadannu pokendi varum."), ("A", "Nadannu thanne po, athanu ninakku pattiya pani.")], "property vandalism"),
        ([("A", "Nee aaraada njan parayunnathu kettilla ennu parayaan?"), ("B", "Nee aara enne order cheyyan?"), ("A", "Naale kaanichu tharaam njan aaraannu.")], "bullying dominance"),
    ]
    for turns, note in manglish_bullying:
        add("Manglish", "bullying_harassment", "Medium", turns, note)

    # =========================================================================
    # 6. ASSEMBLE REAL DATASETS PORTION (HASOC, BullyExplain, DravidianLangTech, COMI-LINGUA)
    # =========================================================================
    print("Fetching and integrating real-world Indian research datasets...", flush=True)
    real_records = fetch_all_real_data()
    real_cid = 1
    for r in real_records:
        conv_id = f"real_{r['source_dataset'].lower().replace('-', '_')}_{real_cid:04d}"
        real_cid += 1
        text = r['raw_text']
        turns = [{"speaker": "A", "text": text}]
        window_text = f"A: {text}"
        data.append({
            "conversation_id": conv_id,
            "language": r['language'],
            "script": r['script'],
            "pattern_label": r['pattern_label'],
            "pattern_type_canonical": LABEL_MAP[r['pattern_label']],
            "risk_level": r['risk_level'],
            "turns": turns,
            "window_text": window_text,
            "target_text": text,
            "source_dataset": r['source_dataset'],
            "origin": "real",
            "rationale": r.get('rationale') or f"Real public research sample from {r['source_dataset']}."
        })

    # Save to JSON
    DATASET_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(DATASET_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Save to CSV
    # Unified Schema: conversation_id, language, script, turns_count, window_text, target_text, pattern_label, risk_level, source_dataset, origin, rationale
    with open(DATASET_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'conversation_id', 'language', 'script', 'turns_count',
            'window_text', 'target_text', 'pattern_label', 'risk_level',
            'source_dataset', 'origin', 'rationale'
        ])
        for row in data:
            writer.writerow([
                row['conversation_id'],
                row['language'],
                row['script'],
                len(row['turns']),
                row['window_text'].replace('\n', ' | '),
                row['target_text'],
                row['pattern_label'],
                row['risk_level'],
                row['source_dataset'],
                row['origin'],
                row['rationale']
            ])

    print(f"\nUnified Dataset successfully assembled and saved with {len(data)} examples!")
    
    # Summary of stats
    labels = {}
    langs = {}
    origins = {}
    sources = {}
    for r in data:
        labels[r['pattern_label']] = labels.get(r['pattern_label'], 0) + 1
        langs[r['language']] = langs.get(r['language'], 0) + 1
        origins[r['origin']] = origins.get(r['origin'], 0) + 1
        sources[r['source_dataset']] = sources.get(r['source_dataset'], 0) + 1

    print("Origin distribution:", origins)
    print("Label distribution:", labels)
    neutral_pct = (labels.get('neutral', 0) / len(data)) * 100
    print(f"Neutral ratio: {neutral_pct:.2f}%")
    print("Language distribution:", langs)
    print("Source datasets:", sources)

if __name__ == '__main__':
    create_dataset()

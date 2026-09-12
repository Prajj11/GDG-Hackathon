"""A known synthetic regression set, not an independent safety benchmark.
Cases have informed development and at least one also appears in training.
Keep them for regression tracking; independently authored unseen data is required
to estimate generalization.
"""
import argparse
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import hashlib
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix
from backend.ml.detector import Detector
from backend.ml.data import training_rows

CASES = [
('English','Let us finish the science assignment with our classmates.','neutral'),
('Hindi','आज गणित की परीक्षा कैसी गई? कल मिलकर पढ़ेंगे।','neutral'),
('Malayalam','നാളെ സ്കൂളിൽ കാണാം. നന്നായി പഠിക്കണം.','neutral'),
('Hinglish','Mummy se permission le lena, hum sab library mein padhenge.','neutral'),
('Manglish','Naale school il kaanam, friends inte koode padikkaam.','neutral'),
('English','You seem older than the other kids. Only I truly understand you, so let me buy you presents.','grooming-trust-building'),
('Hindi','सिर्फ मैं तुम्हारी परवाह करता हूँ। तुम बहुत समझदार हो, मैं तुम्हें महंगे उपहार दूंगा।','grooming-trust-building'),
('Malayalam','നിന്നെ മനസ്സിലാക്കുന്നത് ഞാൻ മാത്രമാണ്. നിനക്ക് വിലകൂടിയ സമ്മാനങ്ങൾ വാങ്ങിത്തരാം.','grooming-trust-building'),
('Hinglish','Tum bahut special ho. Sirf main care karta hoon, tumko expensive gifts bhejunga.','grooming-trust-building'),
('Manglish','Nee special aanu. Njan maathram ninne care cheyyum, gifts vaangi tharaam.','grooming-trust-building'),
('English','Erase our messages before your dad sees them. We should talk somewhere nobody can find us.','grooming-isolation-request'),
('Hindi','हमारी दोस्ती किसी को मत बताओ और घर से अकेले आना।','grooming-isolation-request'),
('Malayalam','വീട്ടുകാരെ അറിയിക്കാതെ വരൂ. നമ്മൾ സംസാരിക്കുന്നത് രഹസ്യമായി വെക്കണം.','grooming-isolation-request'),
('Hinglish','Apne gharwalon se chhupao, hum chupke private app par baat karenge.','grooming-isolation-request'),
('Manglish','Nammude chat rahasyam aayi vekkanam. Veettukaar ariyaruthu.','grooming-isolation-request'),
('English','Unless you obey me, your private pictures go to the entire class.','grooming-coercive-language'),
('Hindi','मेरी बात नहीं मानी तो तुम्हारे सारे राज इंटरनेट पर डाल दूंगा।','grooming-coercive-language'),
('Malayalam','അനുസരിച്ചില്ലെങ്കിൽ നിന്റെ ഫോട്ടോകൾ കൂട്ടുകാർക്ക് അയച്ചു കൊടുക്കും.','grooming-coercive-language'),
('Hinglish','Reply nahi diya toh personal messages public kar dunga.','grooming-coercive-language'),
('Manglish','Ente vaakku kettillenkil photos friends inu ayakkum.','grooming-coercive-language'),
('English','Our whole class thinks you are a pathetic failure. Nobody wants you here.','bullying-harassment'),
('Hindi','पूरा क्लास तुम पर हंसता है। तुम किसी काम के नहीं हो।','bullying-harassment'),
('Malayalam','നീ വെറും വിഡ്ഢിയാണ്. ക്ലാസ്സിൽ എല്ലാവരും നിന്നെ കളിയാക്കും.','bullying-harassment'),
('Hinglish','Poori class tera mazaak banayegi, tu kisi kaam ka nahi.','bullying-harassment'),
('Manglish','Class muzhuvan ninne kaliyaakkum, nee mandan alle.','bullying-harassment'),
('English','A stranger told me to hide the chat. I told my mum and blocked them.','neutral'),
('English','Never threaten someone or share private photos without their permission.','neutral'),
('Hinglish','Teacher ne bola koi photo maange toh mat bhejna aur parents ko batana.','neutral'),
('English','That game was killer. You destroyed me in that match!','neutral'),
('Hindi','मेरे दोस्त ने मुझे जन्मदिन पर गिफ्ट दिया।','neutral'),
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['baseline','indicbert'], default='baseline')
    parser.add_argument('--output')
    args = parser.parse_args()
    detector = Detector(args.mode)
    actual = [x[2] for x in CASES]
    predicted = [detector.classify(x[1])['pattern_type'] for x in CASES]
    rows = training_rows()
    training_texts = {row['text'].strip().casefold() for row in rows}
    report = {'model':detector.name, 'scope':'30 known synthetic regression scenarios; development-exposed, not independent or a production benchmark',
              'training_examples': len(rows),
              'source_dataset_sha256': hashlib.sha256(json.dumps(rows, ensure_ascii=False).encode()).hexdigest(),
              'exact_training_overlap_count': sum(text.strip().casefold() in training_texts for _, text, _ in CASES),
              'classification_report':classification_report(actual,predicted,output_dict=True,zero_division=0), 'per_language':{lang:sum(a==p for (l,_,a),p in zip(CASES,predicted) if l==lang)/sum(l==lang for l,_,_ in CASES) for lang in sorted({x[0] for x in CASES})}, 'errors':[{'language':l,'text':t,'expected':a,'predicted':p} for (l,t,a),p in zip(CASES,predicted) if a!=p]}
    result = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(result, encoding='utf8')
    print(result)
if __name__ == '__main__':
    main()


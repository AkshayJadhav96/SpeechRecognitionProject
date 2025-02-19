import whisper
from better_profanity import profanity

model = whisper.load_model("base")
profanity_filter = profanity
pii_patterns = {
            "Credit Card": r'\b(?:\d[ -]*?){13,16}\b',
            "ATM PIN": r'\b\d{4,6}\b',
            "Email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "Phone Number": r'\b\d{10}\b',
}
sensitive_words = ["password", "atm pin", "credit card","pin","atm"]
categories = {
            "Billing Issues": ["billing","invoice","charge","payment","refund","overcharge","undercharge","statement","fee","transaction","subscription","dues","penalty","late fee","dispute","incorrect charge","unbilled","outstanding balance","due date","autopay","failed payment","processing fee","chargeback","cancellation fee","hidden fees","credit","debit","account balance","payment declined","receipt","service charge","bill", "charge","exchange","discount"],
            "Technical Support": ["troubleshoot","error message","not working","unable to connect","crash","bug","fix issue","resolve problem","support ticket","customer support","it support","help desk","diagnose","configuration issue","compatibility issue","server down","network issue","latency","slow performance","software update","firmware update","patch","malfunction","system failure","blue screen","restart required","connection lost","authentication failed","access denied","data recovery","password reset","account locked","security breach","firewall issue","proxy error","hardware failure","device not recognized","driver update","installation failed","setup issue","runtime error"],
            "Account Management": ["account access", "login issue", "password reset", "update profile", "change email", "change phone number", "account locked", "verify identity", "security question", "two-factor authentication", "deactivate account", "reactivate account", "account suspension", "account termination", "profile settings", "subscription management", "upgrade plan", "downgrade plan", "payment method update", "billing address update", "account recovery", "username change", "merge accounts", "linked accounts", "access permissions", "role management", "account verification", "unauthorized access", "privacy settings", "data deletion request", "terms of service", "account dashboard", "contact support"],
            "General Inquiry": ["information request", "general question", "how to", "guidelines", "terms and conditions", "policy details", "service information", "contact support", "customer service", "faq", "opening hours", "business hours", "pricing details", "availability", "product details", "service status", "order status", "tracking information", "help needed", "assistance required", "directions", "company details", "support channels", "customer feedback", "user manual", "documentation", "report issue", "suggestion", "feature request", "about us", "contact details", "partnership inquiry", "collaboration request"],
            "Cancellation Requests": ["cancel subscription", "cancel order", "membership cancellation", "terminate account", "end service", "stop subscription", "discontinue plan", "request cancellation", "close account", "refund request", "cancellation policy", "early termination", "unsubscribe", "remove service", "void transaction", "delete account", "stop auto-renewal", "cancellation fee", "reverse charge", "withdraw request", "halt service", "stop payment", "cancel booking", "reschedule request", "terminate contract", "cease membership", "opt-out", "service discontinuation", "cancel trial", "deactivate service"],
            "Complaints": ["customer complaint", "file a complaint", "report issue", "bad experience", "poor service", "unsatisfactory response", "not happy", "frustrated", "disappointed", "service failure", "delayed response", "rude behavior", "unresolved issue", "poor quality", "defective product", "damaged item", "incorrect charge", "billing dispute", "refund problem", "scam", "fraud", "unauthorized transaction", "breach of policy", "misleading information", "false advertising", "late delivery", "missing item", "technical glitch", "login problem", "account hacked", "no response", "long wait time", "compensation request", "escalate issue"],
        }
required_phrases = [
            "hello",
            "welcome",
            "good morning",
            "good afternoon",
            "good evening", 
            "thank you for calling",
            "this call is being recorded",
            "is there anything else I can help you with",
        ]
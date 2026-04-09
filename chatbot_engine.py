from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass


STOPWORDS = {
    "a",
    "about",
    "an",
    "are",
    "can",
    "do",
    "for",
    "give",
    "how",
    "i",
    "is",
    "me",
    "of",
    "please",
    "tell",
    "the",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
    "with",
}


SYNONYM_MAP = {
    "tuition": "fees",
    "fee": "fees",
    "payment": "fees",
    "payments": "fees",
    "cost": "fees",
    "price": "fees",
    "charges": "fees",
    "hostel": "accommodation",
    "accommodation": "accommodation",
    "room": "accommodation",
    "rooms": "accommodation",
    "dorm": "accommodation",
    "admission": "admission",
    "apply": "admission",
    "application": "admission",
    "enroll": "admission",
    "eligibility": "admission",
    "exam": "exam",
    "exams": "exam",
    "test": "exam",
    "tests": "exam",
    "schedule": "dates",
    "date": "dates",
    "dates": "dates",
    "scholarship": "scholarship",
    "scholarships": "scholarship",
    "waiver": "scholarship",
    "transport": "bus",
    "bus": "bus",
    "placement": "placement",
    "placements": "placement",
    "package": "package",
    "packages": "package",
    "salary": "package",
    "salaries": "package",
    "recruiters": "company",
    "recruiter": "company",
    "company": "company",
    "companies": "company",
    "job": "placement",
    "jobs": "placement",
    "infrastructure": "campus",
    "campus": "campus",
    "building": "campus",
    "buildings": "campus",
    "facility": "facilities",
    "facilities": "facilities",
    "lab": "laboratory",
    "labs": "laboratory",
    "laboratory": "laboratory",
    "laboratories": "laboratory",
    "library": "library",
    "books": "library",
    "wifi": "internet",
    "internet": "internet",
    "smart": "digital",
    "classroom": "classroom",
    "classrooms": "classroom",
    "canteen": "canteen",
    "cafeteria": "canteen",
    "food": "canteen",
    "sports": "sports",
    "ground": "sports",
    "grounds": "sports",
    "attendance": "attendance",
    "present": "attendance",
    "faculty": "faculty",
    "teachers": "faculty",
    "teacher": "faculty",
    "professor": "faculty",
    "professors": "faculty",
    "course": "program",
    "courses": "program",
    "branch": "program",
    "branches": "program",
    "program": "program",
    "programs": "program",
    "curriculum": "syllabus",
    "syllabus": "syllabus",
    "internship": "internship",
    "internships": "internship",
    "medical": "health",
    "health": "health",
}


INTENT_KEYWORDS = {
    "fees": {"fees"},
    "hostel": {"accommodation"},
    "admission": {"admission", "documents", "criteria"},
    "exam": {"exam", "dates", "semester"},
    "scholarship": {"scholarship"},
    "transport": {"bus", "transport"},
    "placement": {"placement", "career"},
    "infrastructure": {"campus", "facilities", "classroom", "internet"},
    "package": {"package", "placement", "company"},
    "library": {"library"},
    "labs": {"laboratory"},
    "attendance": {"attendance"},
    "canteen": {"canteen"},
    "faculty": {"faculty"},
    "programs": {"program", "syllabus"},
    "internship": {"internship"},
    "health": {"health"},
}


FAQS = [
    {
        "question": "What are the tuition fees for B.Tech?",
        "answer": "The annual tuition fees for B.Tech are Rs. 85,000.",
        "intent": "fees",
    },
    {
        "question": "What are the hostel fees?",
        "answer": "Hostel fees are Rs. 50,000 per year, including accommodation and basic facilities.",
        "intent": "hostel",
    },
    {
        "question": "How can I apply for admission?",
        "answer": "You can apply online through the college admission portal by filling out the application form and uploading the required documents.",
        "intent": "admission",
    },
    {
        "question": "What documents are needed for admission?",
        "answer": "You need mark sheets, ID proof, passport-size photos, transfer certificate, and entrance exam scorecard if applicable.",
        "intent": "admission",
    },
    {
        "question": "When do semester exams start?",
        "answer": "Semester exams usually begin in December for odd semesters and in May for even semesters.",
        "intent": "exam",
    },
    {
        "question": "Is scholarship support available?",
        "answer": "Yes, merit-based and need-based scholarships are available for eligible students.",
        "intent": "scholarship",
    },
    {
        "question": "Is transport available for students?",
        "answer": "Yes, the college provides bus transport on major city routes for enrolled students.",
        "intent": "transport",
    },
    {
        "question": "What is the placement record?",
        "answer": "The college has a strong placement support cell, with regular campus drives and internship opportunities.",
        "intent": "placement",
    },
    {
        "question": "What is the highest placement package?",
        "answer": "The highest recent placement package offered to students is Rs. 12 LPA, depending on branch and recruiter.",
        "intent": "package",
    },
    {
        "question": "What is the average placement package?",
        "answer": "The average placement package is around Rs. 4.5 LPA for eligible students participating in campus recruitment.",
        "intent": "package",
    },
    {
        "question": "Which companies visit for placements?",
        "answer": "Recruiters from IT, core engineering, finance, and service sectors visit the campus, including regional and national companies.",
        "intent": "placement",
    },
    {
        "question": "How is the college infrastructure?",
        "answer": "The campus has spacious classrooms, seminar halls, computer centers, Wi-Fi access, laboratories, and dedicated student activity areas.",
        "intent": "infrastructure",
    },
    {
        "question": "Are smart classrooms available?",
        "answer": "Yes, many classrooms are equipped with projectors and digital teaching tools for interactive learning.",
        "intent": "infrastructure",
    },
    {
        "question": "Does the college have good laboratories?",
        "answer": "Yes, the college has department-wise laboratories for practical sessions, project work, and technical training.",
        "intent": "labs",
    },
    {
        "question": "Is there a library on campus?",
        "answer": "Yes, the central library offers textbooks, reference books, journals, newspapers, and digital learning resources.",
        "intent": "library",
    },
    {
        "question": "What are the attendance rules?",
        "answer": "Students are generally expected to maintain at least 75 percent attendance to appear for semester examinations.",
        "intent": "attendance",
    },
    {
        "question": "Is there a canteen facility?",
        "answer": "Yes, the campus canteen provides hygienic meals, snacks, and beverages at affordable prices.",
        "intent": "canteen",
    },
    {
        "question": "How is the faculty?",
        "answer": "The college has experienced faculty members who support classroom teaching, mentoring, and project guidance.",
        "intent": "faculty",
    },
    {
        "question": "Which courses are offered?",
        "answer": "The college offers undergraduate and postgraduate programs in engineering, management, computer applications, and related disciplines.",
        "intent": "programs",
    },
    {
        "question": "How is the syllabus updated?",
        "answer": "The syllabus is revised periodically to include industry-relevant subjects, practical work, and emerging technologies.",
        "intent": "programs",
    },
    {
        "question": "Are internships provided?",
        "answer": "Yes, the placement and training cell helps students find internships through company tie-ups and project collaborations.",
        "intent": "internship",
    },
    {
        "question": "Is medical support available on campus?",
        "answer": "Basic first-aid and emergency medical support are available on campus, with nearby hospital support when needed.",
        "intent": "health",
    },
    {
        "question": "Are sports facilities available?",
        "answer": "Yes, the campus supports indoor and outdoor sports with grounds and spaces for regular student activities.",
        "intent": "infrastructure",
    },
]


@dataclass
class MatchResult:
    answer: str
    intent: str
    matched_question: str
    similarity: float
    processed_query: list[str]


class FAQChatbot:
    def __init__(self, faqs: list[dict[str, str]]) -> None:
        self.faqs = faqs
        self.documents = [self._build_document(entry) for entry in faqs]
        self.vocabulary = self._build_vocabulary()
        self.idf = self._compute_idf()

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r"[a-zA-Z]+", text.lower())

    def _normalize_token(self, token: str) -> str:
        return SYNONYM_MAP.get(token, token)

    def preprocess(self, text: str) -> list[str]:
        tokens = self._tokenize(text)
        cleaned = []
        for token in tokens:
            if token in STOPWORDS:
                continue
            cleaned.append(self._normalize_token(token))
        return cleaned

    def detect_intent(self, tokens: list[str]) -> str:
        scores: dict[str, int] = {}
        token_set = set(tokens)
        for intent, keywords in INTENT_KEYWORDS.items():
            scores[intent] = len(token_set.intersection(keywords))
        best_intent = max(scores, key=scores.get, default="general")
        return best_intent if scores.get(best_intent, 0) > 0 else "general"

    def _build_document(self, entry: dict[str, str]) -> dict[str, object]:
        combined_text = f"{entry['question']} {entry['intent']}"
        tokens = self.preprocess(combined_text)
        return {
            "question": entry["question"],
            "answer": entry["answer"],
            "intent": entry["intent"],
            "tokens": tokens,
            "term_freq": Counter(tokens),
        }

    def _build_vocabulary(self) -> set[str]:
        vocab: set[str] = set()
        for document in self.documents:
            vocab.update(document["tokens"])
        return vocab

    def _compute_idf(self) -> dict[str, float]:
        document_frequency: dict[str, int] = defaultdict(int)
        for term in self.vocabulary:
            for document in self.documents:
                if term in document["tokens"]:
                    document_frequency[term] += 1

        total_docs = len(self.documents)
        return {
            term: math.log((1 + total_docs) / (1 + freq)) + 1
            for term, freq in document_frequency.items()
        }

    def _tfidf_vector(self, tokens: list[str]) -> dict[str, float]:
        term_freq = Counter(tokens)
        total_terms = len(tokens) or 1
        return {
            term: (count / total_terms) * self.idf.get(term, 1.0)
            for term, count in term_freq.items()
        }

    def _cosine_similarity(
        self, vector_a: dict[str, float], vector_b: dict[str, float]
    ) -> float:
        common_terms = set(vector_a).intersection(vector_b)
        dot_product = sum(vector_a[term] * vector_b[term] for term in common_terms)
        magnitude_a = math.sqrt(sum(value * value for value in vector_a.values()))
        magnitude_b = math.sqrt(sum(value * value for value in vector_b.values()))
        if not magnitude_a or not magnitude_b:
            return 0.0
        return dot_product / (magnitude_a * magnitude_b)

    def answer_query(self, query: str) -> MatchResult:
        tokens = self.preprocess(query)
        intent = self.detect_intent(tokens)
        query_vector = self._tfidf_vector(tokens)

        best_document = None
        best_score = -1.0
        for document in self.documents:
            score = self._cosine_similarity(
                query_vector,
                self._tfidf_vector(document["tokens"]),
            )

            if intent != "general" and document["intent"] == intent:
                score += 0.2

            if score > best_score:
                best_score = score
                best_document = document

        if not best_document or best_score < 0.12:
            return MatchResult(
                answer="I could not find an exact FAQ match. Please ask about admission, fees, hostel, exams, scholarships, transport, placements, packages, infrastructure, library, labs, attendance, canteen, or courses.",
                intent=intent,
                matched_question="No strong match",
                similarity=min(max(best_score, 0.0), 0.999),
                processed_query=tokens,
            )

        return MatchResult(
            answer=best_document["answer"],
            intent=best_document["intent"],
            matched_question=best_document["question"],
            similarity=min(best_score, 0.999),
            processed_query=tokens,
        )

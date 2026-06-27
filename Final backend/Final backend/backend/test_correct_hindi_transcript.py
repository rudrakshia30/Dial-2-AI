"""Tests for Hindi/Hinglish transcript correction (rule-based paths, no API required)."""
import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from app.services.language_filter import user_wants_devanagari
from app.services.correct_hindi_transcript import (
    correct_hindi_transcript,
    detect_input_language,
)
from app.services.repeat_intent import is_repeat_request


class DetectInputLanguageTests(unittest.TestCase):
    def test_english_question(self):
        self.assertEqual(
            detect_input_language("Who is the Prime Minister of India?"),
            "english",
        )

    def test_hindi_devanagari(self):
        self.assertEqual(
            detect_input_language("भारत के प्रधानमंत्री कौन हैं?"),
            "hindi",
        )

    def test_hinglish(self):
        self.assertEqual(
            detect_input_language("Delhi ka mausam kaisa hai?"),
            "hinglish",
        )

    def test_loanword_hindi(self):
        self.assertEqual(
            detect_input_language("Mujhe aaj ki taaza khabar batao."),
            "hindi",
        )


class RuleBasedCorrectionTests(unittest.TestCase):
    def test_pm_garbled_devanagari(self):
        result = asyncio.run(
            correct_hindi_transcript("भारत के प्रदान मुंत्री का क्या नाम है?")
        )
        self.assertIn("pradhan mantri", result.corrected_transcript.lower())

    def test_president_devanagari(self):
        result = asyncio.run(
            correct_hindi_transcript("भारत के राश्ट्रपती कौन है?")
        )
        self.assertIn("rashtrapati", result.corrected_transcript.lower())

    def test_phonetic_president_garble(self):
        result = asyncio.run(
            correct_hindi_transcript("Mastra Pati korn hai?")
        )
        self.assertIn("rashtrapati", result.corrected_transcript.lower())
        self.assertFalse(result.used_llm)

    def test_direct_president_answer(self):
        from app.services.llm import _direct_official_answer

        answer = _direct_official_answer("Bharat ke rashtrapati kaun hain?")
        self.assertIn("Droupadi Murmu", answer)
        self.assertNotIn("Dravindra", answer)

    def test_clean_hindi_skips_llm(self):
        samples = [
            "Kal Delhi ka mausam kaisa rahega?",
            "Mujhe aaj ki taaza khabar batao.",
            "Ahmedabad jaane wali train ka waqt kya hai?",
            "Bazaar mein tamatar ki keemat kya chal rahi hai?",
            "Mere mobile mein recharge nahi hai.",
            "Sarkari yojana ke liye kya zaroori dastavez hain?",
        ]
        for sample in samples:
            with self.subTest(sample=sample):
                result = asyncio.run(correct_hindi_transcript(sample))
                self.assertEqual(result.corrected_transcript, sample)
                self.assertFalse(result.used_llm)

    def test_repeat_phrase_skips_llm(self):
        result = asyncio.run(
            correct_hindi_transcript("Is sawaal ka jawab dobara batao.")
        )
        self.assertTrue(is_repeat_request(result.corrected_transcript))
        self.assertFalse(result.used_llm)

    def test_fallback_on_llm_failure(self):
        with patch(
            "app.services.correct_hindi_transcript._llm_correct_transcript",
            new=AsyncMock(side_effect=RuntimeError("api down")),
        ):
            result = asyncio.run(
                correct_hindi_transcript("भारत के तरदान मंतरी का ग्यानाम है")
            )
        self.assertTrue(result.corrected_transcript)
        self.assertFalse(result.used_llm)


class DevanagariPreferenceTests(unittest.TestCase):
    def test_explicit_devanagari_request(self):
        self.assertTrue(user_wants_devanagari("Devanagari mein jawab do"))


if __name__ == "__main__":
    unittest.main()

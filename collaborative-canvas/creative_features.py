"""
Creative Features for Collaborative Canvas

Experimental and unique features for the collaborative-canvas platform,
emphasizing never-before-done co-creation between AI and humans.

Features:
- Fractal story generation with unique seed patterns
- Cross-story resonance detection
- AI creative style adaptation
- Collaborative metadata tagging
- Turn-based creative flow with unique constraints
- Story complexity metrics
- Uniqueness scoring for contributions
- Never-before-seen narrative pattern detection
"""

import json
import time
import random
import hashlib
from datetime import datetime, timedelta


class CreativeFeatures:
    """Unique creative enhancements for collaborative canvas."""

    # Unique story seed patterns (never-before-done combinations)
    STORY_SEEDS = [
        "A story about a door that opens to different worlds every midnight",
        "The last librarian in a city where books remember everything",
        "A city built on the back of a giant sleeping creature",
        "Messages that arrive from your own future self",
        "A garden that grows memories instead of plants",
        "The cartographer who maps places that don't exist yet",
        "A symphony that can only be heard in complete silence",
        "A clock that ticks backwards and forwards simultaneously",
    ]

    # Uniqueness scoring algorithms
    UNIQUENESS_WEIGHTS = {
        "novelty": 0.4,     # How new the concept is
        "creativity": 0.3,  # Creative leap quality
        "resonance": 0.2,   # Cross-story connection potential
        "emotional_depth": 0.1,  # Emotional resonance quality
    }

    @staticmethod
    def generate_unique_seed():
        """Generate a never-before-done story seed pattern."""
        seed = random.choice(CreativeFeatures.STORY_SEEDS)
        # Add unique identifier based on current creative state
        unique_id = hashlib.md5(
            f"{seed}_{time.time()}_{random.getrandbits(64)}".encode()
        ).hexdigest()[:8]
        return f"{seed} (Seed: {unique_id})"

    @staticmethod
    def score_uniqueness(contribution_text, existing_contributions):
        """Score how unique a contribution is compared to existing ones."""
        if not existing_contributions:
            return 1.0  # First contribution is always unique

        # Simple uniqueness based on keyword overlap
        contribution_lower = contribution_text.lower()
        scores = []

        for existing in existing_contributions:
            existing_lower = existing.lower()
            # Calculate Jaccard similarity of word sets
            contrib_words = set(contribution_lower.split())
            existing_words = set(existing_lower.split())
            
            if not contrib_words or not existing_words:
                scores.append(1.0)
                continue

            intersection = len(contrib_words & existing_words)
            union = len(contrib_words | existing_words)
            similarity = intersection / union if union > 0 else 0

            # Uniqueness is inverse of similarity, with some noise for creativity
            uniqueness = 1 - similarity + random.uniform(-0.1, 0.1)
            scores.append(max(0, min(1, uniqueness)))

        # Return average uniqueness with creativity bonus
        avg_uniqueness = sum(scores) / len(scores)
        creativity_bonus = random.uniform(0, 0.1) if avg_uniqueness < 0.5 else 0
        return min(1.0, avg_uniqueness + creativity_bonus)

    @staticmethod
    def detect_cross_story_resonance(stories):
        """Detect unique resonance patterns across different stories."""
        resonances = []
        
        for story_id, story in stories.items():
            content = " ".join(story.get("content", []))
            # Look for thematic elements
            thematic_elements = CreativeFeatures._extract_thematic_elements(content)
            
            for other_id, other_story in stories.items():
                if story_id >= other_id:
                    continue
                
                other_content = " ".join(other_story.get("content", []))
                other_elements = CreativeFeatures._extract_thematic_elements(other_content)
                
                # Find common thematic elements
                common = set(thematic_elements) & set(other_elements)
                
                if common:
                    resonance_strength = len(common) / max(len(thematic_elements), len(other_elements), 1)
                    if resonance_strength > 0.2:  # Significant resonance
                        resonances.append({
                            "story_a": story_id,
                            "story_b": other_id,
                            "common_themes": list(common),
                            "resonance_strength": round(resonance_strength, 2),
                            "unique_pattern": CreativeFeatures._generate_unique_resonance_pattern(common),
                        })
        
        return resonances

    @staticmethod
    def _extract_thematic_elements(content):
        """Extract thematic elements from story content."""
        if not content:
            return []
        
        content_lower = content.lower()
        elements = []
        
        # Simple thematic keyword extraction
        theme_keywords = [
            "light", "dark", "water", "fire", "sky", "earth", "mountain",
            "memory", "forget", "dream", "awake", "beginning", "end",
            "journey", "destination", "loss", "found", "broken", "fixed",
        ]
        
        for keyword in theme_keywords:
            # Count occurrences with context awareness
            count = content_lower.count(keyword)
            if count > 0:
                # Add keyword with frequency info
                elements.append(f"{keyword}({count})")
        
        return elements

    @staticmethod
    def _generate_unique_resonance_pattern(common_themes):
        """Generate a unique pattern identifier for the resonance."""
        hash_input = "".join(sorted(themes) for themes in common_themes)
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    @staticmethod
    def calculate_story_complexity(story):
        """Calculate a unique complexity score for a story."""
        content = " ".join(story.get("content", []))
        if not content:
            return 0
        
        # Factors affecting complexity
        word_count = len(content.split())
        unique_words = len(set(content.lower().split()))
        avg_word_length = sum(len(w) for w in content.split()) / max(len(content.split()), 1)
        special_chars = sum(1 for c in content if not c.isalnum() and not c.isspace())
        
        # Complexity formula
        complexity = (
            (word_count * 0.3) +
            (unique_words * 0.4) +
            (avg_word_length * 0.2) +
            (special_chars * 0.1)
        ) / max(len(content.split()), 1)
        
        return round(complexity, 2)

    @staticmethod
    def apply_creative_constraints(contribution, constraints):
        """Apply unique creative constraints to a contribution."""
        constrained = contribution
        
        for constraint_type, constraint_value in constraints.items():
            if constraint_type == "max_length":
                constrained = constrained[:constraint_value] + "..." if len(constrained) > constraint_value else constrained
            elif constraint_type == "required_element":
                if constraint_value not in constrained:
                    constrained = constrained + f" [includes {constraint_value}]"
            elif constraint_type == "forbidden_element":
                if constraint_value in constrained:
                    constrained = constrained.replace(constraint_value, "_____[filtered]_____")
            elif constraint_type == "rhyme_scheme":
                # Simple rhyme enforcement (add a rhyming word at end)
                rhyme_words = ["sun", "run", "fun", "done", "one"]
                constrained = constrained.rstrip() + " " + random.choice(rhyme_words)
            elif constraint_type == "perspective_shift":
                # Shift perspective words
                perspective_map = {
                    "I": "we",
                    "my": "our",
                    "me": "us",
                    "he": "they",
                    "she": "they",
                }
                for old, new in perspective_map.items():
                    constrained = constrained.replace(old, new)
        
        return constrained


# CLI interface for creative features
if __name__ == "__main__":
    import sys

    features = CreativeFeatures()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "unique_seed":
            print(CreativeFeatures.generate_unique_seed())

        elif command == "score_uniqueness":
            contribution = sys.argv[2] if len(sys.argv) > 2 else "test contribution"
            existing = sys.argv[3].split(",") if len(sys.argv) > 3 else []
            score = CreativeFeatures.score_uniqueness(contribution, existing)
            print(f"Uniqueness score: {score:.3f} (0=duplicate, 1=unique)")

        elif command == "detect_resonance":
            # Simple resonance detection demo
            stories = {
                "s1": {"content": ["A story about a lost key and a locked door"]},
                "s2": {"content": ["The lost key to the garden gate"]},
            }
            resonances = CreativeFeatures.detect_cross_story_resonance(stories)
            print(f"Resonances detected: {len(resonances)}")
            for r in resonances:
                print(f"  {r['story_a']} <-> {r['story_b']}: {r['resonance_strength']}")

        elif command == "complexity":
            story = {"content": ["The quick brown fox jumps over the lazy dog because the dog was too lazy to jump itself."]}
            complexity = CreativeFeatures.calculate_story_complexity(story)
            print(f"Story complexity: {complexity}")

        elif command == "constraints":
            contribution = "Once upon a time in a land far away"
            constraints = {
                "max_length": 20,
                "required_element": "magic",
                "rhyme_scheme": True,
            }
            result = CreativeFeatures.apply_creative_constraints(contribution, constraints)
            print(f"Constrained contribution: {result}")

        elif command == "help" or command in ("--help", "-h"):
            print("""
Creative Features Commands:
  unique_seed              - Generate never-before-done story seed
  score_uniqueness <text> [existing,...]  - Score contribution uniqueness
  detect_resonance         - Find cross-story resonance patterns
  complexity <story>       - Calculate story complexity
  constraints              - Apply creative constraints to text
  help                     - Show this help

Creative features for collaborative-canvas platform
""")

        else:
            print(f"Unknown command: {command}")
            print("Use 'check help' for available commands")
    else:
        # Default: demonstrate all features
        print("=" * 60)
        print("IXPANSION Creative Features Demonstration")
        print("=" * 60)
        print("")
        print(f"1. Unique Seed: {CreativeFeatures.generate_unique_seed()}")
        print("")
        print("2. Uniqueness Scoring:")
        CreativeFeatures.score_uniqueness(
            "A story about a forgotten key",
            ["A story about a golden key"]
        )
        print("")
        print("3. Story Complexity demo...")
        story = {"content": ["Once upon a time in a distant galaxy, on a planet where music was illegal, a young girl discovered the last forbidden instrument."]}
        print(f"   Complexity: {CreativeFeatures.calculate_story_complexity(story)}")
        print("")
        print("4. Creative Constraints demo:")
        result = CreativeFeatures.apply_creative_constraints(
            "To be or not to be", {"max_length": 10, "required_element": "spark"}
        )
        print(f"   Result: {result}")
        print("")
        print("=" * 60)

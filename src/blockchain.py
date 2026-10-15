import os
import json
import hashlib
import datetime
from typing import Dict, Any, List, Optional, Tuple

class Block:
    def __init__(
        self,
        index: int,
        timestamp: str,
        claim: str,
        verdict: str,
        verification_data: Dict[str, Any],
        previous_hash: str,
        nonce: int = 0,
        block_hash: str = ""
    ):
        self.index = index
        self.timestamp = timestamp
        self.claim = claim
        self.claim_hash = self.hash_claim(claim)
        self.verdict = verdict
        self.verification_data = verification_data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = block_hash if block_hash else self.calculate_hash()

    @staticmethod
    def hash_claim(claim_text: str) -> str:
        """Create a normalized SHA-256 hash of the claim text for lookup."""
        normalized = claim_text.strip().lower()
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    def calculate_hash(self) -> str:
        """Calculate SHA-256 cryptographic hash of block attributes."""
        # Clean copy of data to hash deterministically
        data_summary = {
            "claim": self.claim,
            "verdict": self.verdict,
            "final_trust_score": self.verification_data.get("preliminary_trust_score", 0)
        }
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "claim_hash": self.claim_hash,
            "data_summary": data_summary,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()

    def mine_block(self, difficulty: int = 2):
        """Simple Proof of Work algorithm."""
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self) -> Dict[str, Any]:
        """Convert block instance to dictionary for JSON persistence."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "claim": self.claim,
            "claim_hash": self.claim_hash,
            "verdict": self.verdict,
            "verification_data": self.verification_data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        """Recreate block from dictionary."""
        return cls(
            index=data["index"],
            timestamp=data["timestamp"],
            claim=data["claim"],
            verdict=data["verdict"],
            verification_data=data.get("verification_data", {}),
            previous_hash=data["previous_hash"],
            nonce=data.get("nonce", 0),
            block_hash=data.get("hash", "")
        )


class Blockchain:
    def __init__(self, storage_path: str = "data/blockchain_ledger.json", difficulty: int = 2):
        self.storage_path = storage_path
        self.difficulty = difficulty
        self.chain: List[Block] = []
        self.load_chain()

    def create_genesis_block(self) -> Block:
        """Create initial block of the blockchain."""
        genesis_data = {
            "final_verdict": "GENESIS",
            "preliminary_trust_score": 100,
            "verdict_rationale": "Genesis Block for TruthChain Fake News Verification Ledger."
        }
        genesis = Block(
            index=0,
            timestamp="2026-01-01T00:00:00Z",
            claim="TRUTHCHAIN GENESIS BLOCK",
            verdict="GENESIS",
            verification_data=genesis_data,
            previous_hash="0" * 64,
            nonce=0
        )
        genesis.mine_block(self.difficulty)
        return genesis

    def load_chain(self):
        """Load blockchain ledger from disk if present, else create genesis block."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.chain = [Block.from_dict(b) for b in data]
                if self.is_chain_valid():
                    print(f"Loaded existing Blockchain Ledger with {len(self.chain)} blocks.")
                    return
                else:
                    print("Warning: Existing chain file invalid/corrupted. Initializing new chain.")
            except Exception as e:
                print(f"Error loading blockchain file: {e}. Initializing new chain.")

        # Re-initialize genesis chain
        self.chain = [self.create_genesis_block()]
        self.save_chain()

    def save_chain(self):
        """Persist current blockchain to disk."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=2)

    def get_latest_block(self) -> Block:
        """Return latest block in chain."""
        return self.chain[-1]

    @staticmethod
    def normalize_claim_tokens(claim_text: str) -> set:
        """Normalize claim text and replace common acronym synonyms (e.g. CM -> chief minister)."""
        text = claim_text.strip().lower()
        # Expand common synonyms
        synonyms = {
            "cm": "chief minister",
            "pm": "prime minister",
            "tn": "tamil nadu",
            "tamilnadu": "tamil nadu",
            "usa": "united states"
        }
        for k, v in synonyms.items():
            text = text.replace(k, v)
        
        # Extract alphanumeric words
        words = set("".join([c if c.isalnum() or c.isspace() else "" for c in text]).split())
        return words

    def compute_semantic_similarity(self, claim1: str, claim2: str) -> float:
        """Compute semantic overlap score between two claims."""
        c1_norm = claim1.strip().lower()
        c2_norm = claim2.strip().lower()

        if c1_norm == c2_norm:
            return 1.0

        w1 = self.normalize_claim_tokens(claim1)
        w2 = self.normalize_claim_tokens(claim2)

        if not w1 or not w2:
            return 0.0

        intersection = w1.intersection(w2)
        union = w1.union(w2)
        jaccard = len(intersection) / len(union) if union else 0.0

        # Sequence matcher ratio
        import difflib
        seq_ratio = difflib.SequenceMatcher(None, c1_norm, c2_norm).ratio()

        return max(jaccard, seq_ratio)

    def find_claim(self, claim_text: str, similarity_threshold: float = 0.65) -> Optional[Tuple[Block, Dict[str, Any]]]:
        """
        Search if exact, normalized, or semantically equivalent claim text is recorded in the blockchain.
        Returns (Block, verification_data) if found, else None.
        """
        search_hash = Block.hash_claim(claim_text)
        search_normalized = claim_text.strip().lower()

        # Iterate from newest to oldest blocks (skip genesis)
        best_match_block = None
        best_match_score = 0.0

        for block in reversed(self.chain[1:]):
            from src.patches import is_strict_cache_match
            # 1. Exact string or hash match with TTL validation
            if block.claim_hash == search_hash or block.claim.strip().lower() == search_normalized:
                is_valid, exact_score = is_strict_cache_match(claim_text, block, sim_score=1.0)
                if is_valid:
                    best_match_block = block
                    best_match_score = exact_score
                    break

            # 2. Semantic similarity match for rephrased claims with entity and TTL checks
            sim = self.compute_semantic_similarity(claim_text, block.claim)
            is_valid, matched_score = is_strict_cache_match(claim_text, block, sim_score=sim, similarity_threshold=similarity_threshold)
            if is_valid and matched_score > best_match_score:
                best_match_score = matched_score
                best_match_block = block

        if best_match_block and best_match_score >= similarity_threshold:
            retrieved_data = dict(best_match_block.verification_data)
            retrieved_data["blockchain_info"] = {
                "is_cached_in_blockchain": True,
                "semantic_match_score": round(best_match_score * 100, 1),
                "matched_claim": best_match_block.claim,
                "block_index": best_match_block.index,
                "block_hash": best_match_block.hash,
                "previous_hash": best_match_block.previous_hash,
                "verified_at": best_match_block.timestamp,
                "nonce": best_match_block.nonce
            }
            print(f"Blockchain Hit! Match score: {round(best_match_score * 100, 1)}% between '{claim_text}' and '{best_match_block.claim}'")
            return best_match_block, retrieved_data

        return None

    def add_claim_block(self, claim_text: str, verification_result: Dict[str, Any]) -> Block:
        """Mine and append a new block containing verified claim results."""
        latest_block = self.get_latest_block()
        verdict = verification_result.get("final_verdict", "UNKNOWN")
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        import config
        verification_result["pipeline_version"] = getattr(config, "PIPELINE_VERSION", "2.0.0")

        new_block = Block(
            index=len(self.chain),
            timestamp=timestamp,
            claim=claim_text,
            verdict=verdict,
            verification_data=verification_result,
            previous_hash=latest_block.hash
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.save_chain()
        print(f"Mined & Added Block #{new_block.index} with hash: {new_block.hash[:16]}...")
        return new_block

    def is_chain_valid(self) -> bool:
        """Cryptographically audit the full chain for tampering."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # 1. Verify stored block hash matches calculated hash
            if current.hash != current.calculate_hash():
                print(f"Blockchain Audit Error: Block #{current.index} hash mismatch!")
                return False

            # 2. Verify link to previous block
            if current.previous_hash != previous.hash:
                print(f"Blockchain Audit Error: Block #{current.index} previous_hash link broken!")
                return False

            # 3. Check proof of work
            if not current.hash.startswith("0" * self.difficulty):
                print(f"Blockchain Audit Error: Block #{current.index} fails Proof of Work difficulty!")
                return False

        return True

    def get_chain_summary(self) -> Dict[str, Any]:
        """Return chain status overview for UI dashboard."""
        return {
            "is_valid": self.is_chain_valid(),
            "total_blocks": len(self.chain),
            "difficulty": self.difficulty,
            "latest_block_hash": self.get_latest_block().hash,
            "blocks": [b.to_dict() for b in self.chain]
        }

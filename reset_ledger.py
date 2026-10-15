import os
import sys
import shutil
import datetime
import argparse
from typing import List

# Ensure project root in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.blockchain import Blockchain


def reset_ledger(confirm: bool = False):
    if not confirm:
        print("=" * 70)
        print("SAFETY WARNING: This operation will backup and clear the active blockchain ledger.")
        print("To proceed, you must provide the '--confirm' flag:")
        print("    python reset_ledger.py --confirm")
        print("=" * 70)
        sys.exit(1)

    # 1. Generate UTC timestamp for backup directory
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    ts_str = now_utc.strftime("%Y%m%d_%H%M%SZ")
    backup_dir = os.path.join(BASE_DIR, "backup", f"chain_{ts_str}")
    os.makedirs(backup_dir, exist_ok=True)

    ledger_path = os.path.join(BASE_DIR, "data", "blockchain_ledger.json")

    # 2. Back up active blockchain ledger if it exists
    backed_up_files: List[str] = []
    if os.path.exists(ledger_path):
        dest_ledger = os.path.join(backup_dir, "blockchain_ledger.json")
        shutil.copy2(ledger_path, dest_ledger)
        backed_up_files.append(dest_ledger)

    # Backup any additional cache or db files if present
    for root, dirs, files in os.walk(os.path.join(BASE_DIR, "data")):
        for f in files:
            if f.endswith((".db", ".sqlite", ".cache")):
                src_f = os.path.join(root, f)
                rel_f = os.path.relpath(src_f, BASE_DIR)
                dest_f = os.path.join(backup_dir, os.path.basename(f))
                shutil.copy2(src_f, dest_f)
                backed_up_files.append(dest_f)

    print("=" * 70)
    print(f"BACKUP COMPLETED:")
    print(f"  Backup Directory: {backup_dir}")
    for bf in backed_up_files:
        print(f"  Saved: {bf}")
    print("=" * 70)

    # 3. Clear and regenerate Genesis block only
    bc = Blockchain(storage_path=ledger_path, difficulty=2)
    genesis_block = bc.create_genesis_block()
    bc.chain = [genesis_block]
    bc.save_chain()

    # 4. Clear any Python cache files
    pycache_count = 0
    for root, dirs, files in os.walk(BASE_DIR):
        if "__pycache__" in dirs:
            pycache_dir = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(pycache_dir)
                pycache_count += 1
            except Exception:
                pass

    # 5. Verify the reset chain
    is_valid = bc.is_chain_valid()
    print("LEDGER RESET STATUS:")
    print(f"  Total blocks: {len(bc.chain)}")
    print(f"  Genesis Block Hash: {genesis_block.hash}")
    print(f"  Chain Valid: {is_valid}")
    print(f"  Proof of Work Difficulty: {bc.difficulty}")
    print(f"  PyCache cleared: {pycache_count} directories")
    print("=" * 70)

    if not is_valid:
        print("ERROR: Newly generated genesis block failed validation!")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup and reset TruthChain blockchain ledger.")
    parser.add_argument("--confirm", action="store_true", help="Confirm resetting the active blockchain ledger")
    args = parser.parse_args()

    reset_ledger(confirm=args.confirm)

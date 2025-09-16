import random
import string
import time


def generate_transaction_code():
    # Exemple : MPESA-8F9D2KQ3
    prefix = "MPESA"
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}-{code}"


def simulate_mobile_money(amount: float, user_phone: str) -> dict:
    """
    Simule un paiement Mobile Money (M-Pesa, Airtel Money, etc.)
    """
    # Pause pour simuler le délai de transaction
    time.sleep(2)

    # Générer un ID unique de transaction
    transaction_id = "MM-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    # Simulation de succès/échec
    success = random.choice([True, True, True, False])  # 75% de chances succès

    if success:
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "message": f"Paiement de {amount} USD confirmé via Mobile Money."
        }
    else:
        return {
            "status": "failed",
            "transaction_id": transaction_id,
            "message": "Échec du paiement, solde insuffisant."
        }

from services.launch_copilot_service import evaluate_launch
from services.adapters import get_adapter

def test_launch_copilot_verdicts():
    p = get_adapter().projects().iloc[0]['project']
    hot = evaluate_launch(project=p, my_price_psf=15000)
    cool = evaluate_launch(project=p, my_price_psf=6500)
    assert hot.threat_score >= cool.threat_score
    assert hot.verdict in {'GO', 'HOLD', 'NO-GO'}
    assert len(hot.actions) == 3

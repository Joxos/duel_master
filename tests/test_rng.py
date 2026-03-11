from duel_engine.rng import RNG, deterministic_shuffle_hash


def test_deterministic_shuffle_same_seed_produces_same_hash():
    values = [f"card_{i}" for i in range(20)]

    hash_one = deterministic_shuffle_hash(seed=1337, values=values)
    hash_two = deterministic_shuffle_hash(seed=1337, values=values)

    assert hash_one == hash_two


def test_deterministic_shuffle_different_seed_produces_different_hash():
    values = [f"card_{i}" for i in range(20)]

    hash_one = deterministic_shuffle_hash(seed=1337, values=values)
    hash_two = deterministic_shuffle_hash(seed=1338, values=values)

    assert hash_one != hash_two


def test_choice_and_randint_are_deterministic_for_seed():
    rng_one = RNG(42)
    rng_two = RNG(42)

    seq = ["a", "b", "c", "d"]
    draws_one = [rng_one.choice(seq) for _ in range(8)]
    draws_two = [rng_two.choice(seq) for _ in range(8)]

    assert draws_one == draws_two
    assert rng_one.randint(1, 100) == rng_two.randint(1, 100)

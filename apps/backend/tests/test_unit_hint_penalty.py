"""Regra de desconto por dicas (ADR-013): custo por nível, inteiro, limitado a 10% do total."""

from __future__ import annotations

import pytest
from app.progress.service import hint_cost, hint_penalty, hint_penalty_cap


def test_cost_by_level() -> None:
    assert [hint_cost(lv) for lv in (1, 2, 3, 4)] == [0, 1, 2, 2]


@pytest.mark.parametrize(
    ("levels", "max_score", "expected"),
    [
        ([], 100, 0),
        ([1, 1, 1], 100, 0),  # só primeiras dicas: grátis
        ([1, 2, 3], 100, 3),  # uma etapa com as três dicas
        ([1, 2, 3] * 5, 100, 10),  # LAB-001 com as 15 dicas: 15 pontos, limitado a 10
        ([1, 2, 3], 25, 2),  # teto = piso(10% de 25) = 2
        ([1, 2], 9, 0),  # total pequeno: teto 0
    ],
)
def test_penalty_is_integer_and_capped(levels: list[int], max_score: int, expected: int) -> None:
    assert hint_penalty(levels, max_score) == expected
    assert hint_penalty(levels, max_score) <= hint_penalty_cap(max_score) <= max_score // 10

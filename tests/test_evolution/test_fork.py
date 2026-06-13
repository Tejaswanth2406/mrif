"""Tests for ForkManager."""
from __future__ import annotations


def test_create_fork(fork_manager):
    fork = fork_manager.create_fork(
        parent_id="CORE-001",
        hypothesis="More dimensions = better results",
        parameters={"space_dims": 4},
    )
    assert fork is not None
    assert fork.parent_id == "CORE-001"


def test_fork_is_active_by_default(fork_manager):
    fork = fork_manager.create_fork("parent", "h", {})
    assert fork.is_active is True


def test_active_count(fork_manager):
    fork_manager.create_fork("p", "h1", {})
    fork_manager.create_fork("p", "h2", {})
    assert fork_manager.active_count() == 2


def test_retire_fork(fork_manager):
    fork = fork_manager.create_fork("p", "h", {})
    fork_manager.retire(fork.fork_id)
    assert fork_manager.active_count() == 0


def test_update_fitness(fork_manager):
    fork = fork_manager.create_fork("p", "h", {})
    fork_manager.update_fitness(fork.fork_id, 0.88)
    assert fork_manager.all_forks()[0].fitness == 0.88


def test_best_returns_highest_fitness(fork_manager):
    f1 = fork_manager.create_fork("p", "h1", {})
    f2 = fork_manager.create_fork("p", "h2", {})
    fork_manager.update_fitness(f1.fork_id, 0.3)
    fork_manager.update_fitness(f2.fork_id, 0.9)
    best = fork_manager.best(1)
    assert best[0].fork_id == f2.fork_id


def test_best_n(fork_manager):
    for i in range(5):
        f = fork_manager.create_fork("p", f"h{i}", {})
        fork_manager.update_fitness(f.fork_id, i * 0.1)
    top3 = fork_manager.best(3)
    assert len(top3) == 3
    assert top3[0].fitness >= top3[1].fitness >= top3[2].fitness


def test_best_excludes_retired(fork_manager):
    f1 = fork_manager.create_fork("p", "h1", {})
    f2 = fork_manager.create_fork("p", "h2", {})
    fork_manager.update_fitness(f1.fork_id, 0.99)
    fork_manager.retire(f1.fork_id)
    best = fork_manager.best(1)
    assert best[0].fork_id == f2.fork_id


def test_all_forks(fork_manager):
    fork_manager.create_fork("p", "h1", {})
    fork_manager.create_fork("p", "h2", {})
    assert len(fork_manager.all_forks()) == 2


def test_retire_nonexistent_no_error(fork_manager):
    fork_manager.retire("ghost-id")  # should not raise


def test_fork_stores_parameters(fork_manager):
    fork = fork_manager.create_fork("p", "h", {"alpha": 0.01, "beta": 0.99})
    assert fork.parameters["alpha"] == 0.01

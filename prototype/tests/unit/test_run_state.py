"""Unit tests for the Run State system (Phase A: data model)."""

from __future__ import annotations

from roguelike_sprawl.engine.state import AppState
from roguelike_sprawl.matrix.node import IceKind, NodeKind, ZoneDepth
from roguelike_sprawl.run import (
    DEFAULT_FLOW,
    ObjectiveKind,
    RunState,
    Stage,
    check_combat_victory,
    check_extract_complete,
    check_npc_talk_complete,
    check_objective_at_node,
    ensure_run_state,
    get_stage_info,
    resolve_target_for_stage,
    start_new_run,
    start_run,
)


class TestStageEnum:
    """Stage enum has the expected values."""

    def test_stage_values(self) -> None:
        """All expected stages exist."""
        assert Stage.PENDING.value == "pending"
        assert Stage.MEET_NPC.value == "meet_npc"
        assert Stage.EXTRACT_DATA.value == "extract_data"
        assert Stage.DEFEAT_ICE.value == "defeat_ice"
        assert Stage.COMPLETE.value == "complete"
        assert Stage.FAILED.value == "failed"

    def test_stage_is_strenum(self) -> None:
        """Stage is a string enum (comparable to str)."""
        assert Stage.MEET_NPC == "meet_npc"
        assert f"current: {Stage.MEET_NPC}" == "current: meet_npc"


class TestObjectiveKind:
    """ObjectiveKind enum values."""

    def test_objective_kinds(self) -> None:
        """All expected kinds exist."""
        assert ObjectiveKind.NPC.value == "npc"
        assert ObjectiveKind.DATA.value == "data"
        assert ObjectiveKind.ICE.value == "ice"
        assert ObjectiveKind.NONE.value == "none"


class TestStageInfo:
    """StageInfo dataclass."""

    def test_get_stage_info_meet_npc(self) -> None:
        """MEET_NPC stage has correct info."""
        info = get_stage_info(Stage.MEET_NPC)
        assert info.stage is Stage.MEET_NPC
        assert info.objective_kind is ObjectiveKind.NPC
        assert info.next_stage is Stage.EXTRACT_DATA
        assert "construct" in info.hint.lower() or "npc" in info.hint.lower()

    def test_get_stage_info_extract(self) -> None:
        """EXTRACT_DATA stage has DATA objective."""
        info = get_stage_info(Stage.EXTRACT_DATA)
        assert info.objective_kind is ObjectiveKind.DATA
        assert info.next_stage is Stage.DEFEAT_ICE

    def test_get_stage_info_defeat(self) -> None:
        """DEFEAT_ICE stage has ICE objective."""
        info = get_stage_info(Stage.DEFEAT_ICE)
        assert info.objective_kind is ObjectiveKind.ICE
        assert info.next_stage is Stage.COMPLETE

    def test_get_stage_info_complete(self) -> None:
        """COMPLETE stage has no next."""
        info = get_stage_info(Stage.COMPLETE)
        assert info.objective_kind is ObjectiveKind.NONE
        assert info.next_stage is None

    def test_get_stage_info_pending(self) -> None:
        """PENDING stage has no objective."""
        info = get_stage_info(Stage.PENDING)
        assert info.objective_kind is ObjectiveKind.NONE
        assert info.next_stage is None

    def test_get_stage_info_failed(self) -> None:
        """FAILED stage has no next."""
        info = get_stage_info(Stage.FAILED)
        assert info.objective_kind is ObjectiveKind.NONE
        assert info.next_stage is None

    def test_default_flow_order(self) -> None:
        """DEFAULT_FLOW goes MEET_NPC → EXTRACT → DEFEAT → COMPLETE."""
        # Find indices
        flow = {info.stage: info for info in DEFAULT_FLOW}
        assert flow[Stage.MEET_NPC].next_stage is Stage.EXTRACT_DATA
        assert flow[Stage.EXTRACT_DATA].next_stage is Stage.DEFEAT_ICE
        assert flow[Stage.DEFEAT_ICE].next_stage is Stage.COMPLETE


class TestRunStateInit:
    """RunState initialization."""

    def test_default_init(self) -> None:
        """New RunState starts at PENDING."""
        rs = RunState()
        assert rs.current_stage is Stage.PENDING
        assert rs.completed_stages == ()
        assert rs.pending_advance is False
        assert rs.current_target_node is None

    def test_start_run(self) -> None:
        """start_run creates fresh RunState at default stage (MEET_NPC)."""
        rs = start_run()
        assert rs.current_stage is Stage.MEET_NPC

    def test_start_run_with_initial_stage(self) -> None:
        """start_run accepts initial stage."""
        rs = start_run(initial_stage=Stage.MEET_NPC)
        assert rs.current_stage is Stage.MEET_NPC

    def test_reset(self) -> None:
        """reset() returns to PENDING."""
        rs = start_run(initial_stage=Stage.MEET_NPC)
        rs.completed_stages = (Stage.MEET_NPC,)
        rs.current_target_node = "n1"
        rs.reset()
        assert rs.current_stage is Stage.PENDING
        assert rs.completed_stages == ()
        assert rs.current_target_node is None


class TestRunStateProperties:
    """Property methods on RunState."""

    def test_is_complete_at_complete(self) -> None:
        """is_complete True at COMPLETE stage."""
        rs = RunState(current_stage=Stage.COMPLETE)
        assert rs.is_complete() is True

    def test_is_complete_at_failed(self) -> None:
        """is_complete True at FAILED stage."""
        rs = RunState(current_stage=Stage.FAILED)
        assert rs.is_complete() is True

    def test_is_complete_false_in_progress(self) -> None:
        """is_complete False during active stages."""
        for stage in (Stage.PENDING, Stage.MEET_NPC, Stage.EXTRACT_DATA, Stage.DEFEAT_ICE):
            rs = RunState(current_stage=stage)
            assert rs.is_complete() is False, f"{stage} should not be complete"

    def test_is_in_progress(self) -> None:
        """is_in_progress True for active stages only."""
        for stage in (Stage.MEET_NPC, Stage.EXTRACT_DATA, Stage.DEFEAT_ICE):
            rs = RunState(current_stage=stage)
            assert rs.is_in_progress() is True, f"{stage} should be in progress"

        for stage in (Stage.PENDING, Stage.COMPLETE, Stage.FAILED):
            rs = RunState(current_stage=stage)
            assert rs.is_in_progress() is False

    def test_objective_kind(self) -> None:
        """objective_kind delegates to current_info()."""
        rs = RunState(current_stage=Stage.MEET_NPC)
        assert rs.objective_kind() is ObjectiveKind.NPC

        rs = RunState(current_stage=Stage.DEFEAT_ICE)
        assert rs.objective_kind() is ObjectiveKind.ICE

    def test_hint(self) -> None:
        """hint() returns non-empty string for every stage."""
        for stage in Stage:
            rs = RunState(current_stage=stage)
            hint = rs.hint()
            assert isinstance(hint, str)
            assert len(hint) > 0


class TestRunStateMarkAdvance:
    """mark_advance() transitions to next stage."""

    def test_advance_meet_npc_to_extract(self) -> None:
        """MEET_NPC → EXTRACT_DATA."""
        rs = RunState(current_stage=Stage.MEET_NPC)
        rs.mark_advance()
        assert rs.current_stage is Stage.EXTRACT_DATA
        assert Stage.MEET_NPC in rs.completed_stages

    def test_advance_extract_to_defeat(self) -> None:
        """EXTRACT_DATA → DEFEAT_ICE."""
        rs = RunState(current_stage=Stage.EXTRACT_DATA)
        rs.mark_advance()
        assert rs.current_stage is Stage.DEFEAT_ICE
        assert Stage.EXTRACT_DATA in rs.completed_stages

    def test_advance_defeat_to_complete(self) -> None:
        """DEFEAT_ICE → COMPLETE."""
        rs = RunState(current_stage=Stage.DEFEAT_ICE)
        rs.mark_advance()
        assert rs.current_stage is Stage.COMPLETE
        assert Stage.DEFEAT_ICE in rs.completed_stages

    def test_advance_clears_target(self) -> None:
        """advancing clears current_target_node."""
        rs = RunState(current_stage=Stage.MEET_NPC, current_target_node="n1")
        rs.mark_advance()
        assert rs.current_target_node is None

    def test_advance_sets_pending_flag(self) -> None:
        """mark_advance sets pending_advance True."""
        rs = RunState(current_stage=Stage.MEET_NPC)
        rs.mark_advance()
        assert rs.pending_advance is True

    def test_advance_does_not_stop_at_intermediate(self) -> None:
        """Calling mark_advance twice in a row keeps advancing.

        This is the new behaviour: mark_advance is NOT idempotent.
        The call site is responsible for guarding with check_* helpers.
        Two consecutive mark_advance calls without such guards would
        skip a stage.
        """
        rs = RunState(current_stage=Stage.MEET_NPC)
        rs.mark_advance()
        assert rs.current_stage is Stage.EXTRACT_DATA
        rs.mark_advance()
        # Without guards, we'd now be at DEFEAT_ICE.
        assert rs.current_stage is Stage.DEFEAT_ICE
        # completed_stages records both (caller should guard in practice).
        assert Stage.MEET_NPC in rs.completed_stages
        assert Stage.EXTRACT_DATA in rs.completed_stages

    def test_advance_records_completed_each_call(self) -> None:
        """Each mark_advance call appends the current stage to completed_stages."""
        rs = RunState(current_stage=Stage.MEET_NPC)
        rs.mark_advance()
        rs.mark_advance()
        # MEET_NPC and EXTRACT_DATA both in completed
        assert Stage.MEET_NPC in rs.completed_stages
        assert Stage.EXTRACT_DATA in rs.completed_stages
        # But not duplicated within a single stage
        assert rs.completed_stages.count(Stage.MEET_NPC) == 1
        assert rs.completed_stages.count(Stage.EXTRACT_DATA) == 1

    def test_advance_at_complete_noop(self) -> None:
        """mark_advance at COMPLETE is no-op."""
        rs = RunState(current_stage=Stage.COMPLETE)
        rs.mark_advance()
        assert rs.current_stage is Stage.COMPLETE
        assert rs.completed_stages == ()

    def test_advance_at_failed_noop(self) -> None:
        """mark_advance at FAILED is no-op."""
        rs = RunState(current_stage=Stage.FAILED)
        rs.mark_advance()
        assert rs.current_stage is Stage.FAILED

    def test_advance_at_pending_noop(self) -> None:
        """mark_advance at PENDING is no-op."""
        rs = RunState(current_stage=Stage.PENDING)
        rs.mark_advance()
        assert rs.current_stage is Stage.PENDING


class TestRunStateConfirmAdvance:
    """confirm_advance() clears pending flag."""

    def test_confirm_clears_pending(self) -> None:
        """confirm_advance sets pending_advance to False."""
        rs = RunState(current_stage=Stage.MEET_NPC)
        rs.mark_advance()
        assert rs.pending_advance is True
        rs.confirm_advance()
        assert rs.pending_advance is False
        # Stage is preserved
        assert rs.current_stage is Stage.EXTRACT_DATA

    def test_can_advance_again_after_confirm(self) -> None:
        """After confirm_advance, next mark_advance moves forward."""
        rs = RunState(current_stage=Stage.MEET_NPC)
        rs.mark_advance()
        rs.confirm_advance()
        # Now manually move back to MEET_NPC and try again
        rs.current_stage = Stage.MEET_NPC
        rs.mark_advance()
        assert rs.current_stage is Stage.EXTRACT_DATA


class TestRunStateMarkFailed:
    """mark_failed() sets run to FAILED."""

    def test_mark_failed(self) -> None:
        """mark_failed transitions to FAILED."""
        rs = RunState(current_stage=Stage.MEET_NPC)
        rs.mark_failed()
        assert rs.current_stage is Stage.FAILED
        assert rs.is_complete() is True
        assert Stage.MEET_NPC in rs.completed_stages

    def test_mark_failed_clears_target(self) -> None:
        """mark_failed clears current_target_node."""
        rs = RunState(current_stage=Stage.MEET_NPC, current_target_node="n1")
        rs.mark_failed()
        assert rs.current_target_node is None

    def test_mark_failed_pending_advance(self) -> None:
        """mark_failed sets pending_advance True (for death screen)."""
        rs = RunState(current_stage=Stage.MEET_NPC)
        rs.mark_failed()
        assert rs.pending_advance is True


class TestRunStateSetTarget:
    """set_target() and mark_visited() helpers."""

    def test_set_target(self) -> None:
        """set_target sets current_target_node."""
        rs = RunState()
        rs.set_target("n1")
        assert rs.current_target_node == "n1"

    def test_set_target_none(self) -> None:
        """set_target(None) clears the target."""
        rs = RunState(current_target_node="n1")
        rs.set_target(None)
        assert rs.current_target_node is None

    def test_mark_visited(self) -> None:
        """mark_visited sets last_visited_node."""
        rs = RunState()
        rs.mark_visited("n1")
        assert rs.last_visited_node == "n1"


class TestEnsureRunState:
    """ensure_run_state() lazy initializer."""

    def test_creates_if_none(self) -> None:
        """ensure_run_state creates RunState when state.run_state is None."""
        state = AppState()
        state.run_state = None
        rs = ensure_run_state(state)
        assert rs is not None
        assert state.run_state is rs

    def test_returns_existing(self) -> None:
        """ensure_run_state returns existing RunState."""
        state = AppState()
        existing = start_run(initial_stage=Stage.MEET_NPC)
        state.run_state = existing
        rs = ensure_run_state(state)
        assert rs is existing


class TestStartNewRun:
    """start_new_run() factory."""

    def test_start_new_run_default(self) -> None:
        """start_new_run defaults to MEET_NPC."""
        state = AppState()
        rs = start_new_run(state)
        assert rs.current_stage is Stage.MEET_NPC
        assert state.run_state is rs

    def test_start_new_run_with_stage(self) -> None:
        """start_new_run accepts custom initial stage."""
        state = AppState()
        rs = start_new_run(state, initial_stage=Stage.DEFEAT_ICE)
        assert rs.current_stage is Stage.DEFEAT_ICE


class TestResolveTargetForStage:
    """resolve_target_for_stage() finds the right node in the matrix."""

    def _make_matrix(self):
        """Build a small matrix with NPC, DATA, ICE nodes."""
        from roguelike_sprawl.matrix.node import Node

        nodes = [
            Node(id="entry", label="Entry", kind=NodeKind.ENTRY, zone=ZoneDepth.SURFACE),
            Node(id="npc1", label="Dixie", kind=NodeKind.CONSTRUCT, zone=ZoneDepth.SURFACE),
            Node(id="data1", label="Data", kind=NodeKind.DATA, zone=ZoneDepth.SURFACE),
            Node(id="ice1", label="ICE", kind=NodeKind.ICE, zone=ZoneDepth.SURFACE, ice=IceKind.STANDARD),
        ]
        edges = ()
        return nodes, edges

    def test_resolve_npc_target(self) -> None:
        """NPC stage finds CONSTRUCT node."""
        from roguelike_sprawl.matrix.graph import MatrixGraph

        nodes, edges = self._make_matrix()
        matrix = MatrixGraph(nodes=nodes, edges=edges, entry_id="entry")
        rs = RunState(current_stage=Stage.MEET_NPC)

        target = resolve_target_for_stage(rs, matrix)

        assert target == "npc1"

    def test_resolve_data_target(self) -> None:
        """DATA stage finds DATA node."""
        from roguelike_sprawl.matrix.graph import MatrixGraph

        nodes, edges = self._make_matrix()
        matrix = MatrixGraph(nodes=nodes, edges=edges, entry_id="entry")
        rs = RunState(current_stage=Stage.EXTRACT_DATA)

        target = resolve_target_for_stage(rs, matrix)

        assert target == "data1"

    def test_resolve_ice_target(self) -> None:
        """ICE stage finds ICE node."""
        from roguelike_sprawl.matrix.graph import MatrixGraph

        nodes, edges = self._make_matrix()
        matrix = MatrixGraph(nodes=nodes, edges=edges, entry_id="entry")
        rs = RunState(current_stage=Stage.DEFEAT_ICE)

        target = resolve_target_for_stage(rs, matrix)

        assert target == "ice1"

    def test_resolve_no_target_for_pending(self) -> None:
        """PENDING stage has no target."""
        from roguelike_sprawl.matrix.graph import MatrixGraph

        nodes, edges = self._make_matrix()
        matrix = MatrixGraph(nodes=nodes, edges=edges, entry_id="entry")
        rs = RunState(current_stage=Stage.PENDING)

        target = resolve_target_for_stage(rs, matrix)

        assert target is None

    def test_resolve_no_target_for_complete(self) -> None:
        """COMPLETE stage has no target."""
        from roguelike_sprawl.matrix.graph import MatrixGraph

        nodes, edges = self._make_matrix()
        matrix = MatrixGraph(nodes=nodes, edges=edges, entry_id="entry")
        rs = RunState(current_stage=Stage.COMPLETE)

        target = resolve_target_for_stage(rs, matrix)

        assert target is None

    def test_resolve_returns_none_for_empty_matrix(self) -> None:
        """Empty matrix returns None."""
        from roguelike_sprawl.matrix.graph import MatrixGraph

        matrix = MatrixGraph(nodes=(), edges=(), entry_id="")
        rs = RunState(current_stage=Stage.MEET_NPC)

        target = resolve_target_for_stage(rs, matrix)

        assert target is None

    def test_resolve_returns_none_for_no_matching_node(self) -> None:
        """Matrix without matching node kind returns None."""
        from roguelike_sprawl.matrix.graph import MatrixGraph
        from roguelike_sprawl.matrix.node import Node

        nodes = [
            Node(id="entry", label="Entry", kind=NodeKind.ENTRY, zone=ZoneDepth.SURFACE),
        ]
        matrix = MatrixGraph(nodes=tuple(nodes), edges=(), entry_id="entry")
        rs = RunState(current_stage=Stage.MEET_NPC)

        target = resolve_target_for_stage(rs, matrix)

        assert target is None


class TestCheckObjectiveAtNode:
    """check_objective_at_node() validates stage completion."""

    def _make_matrix(self):
        from roguelike_sprawl.matrix.graph import MatrixGraph
        from roguelike_sprawl.matrix.node import Node

        nodes = (
            Node(id="entry", label="Entry", kind=NodeKind.ENTRY, zone=ZoneDepth.SURFACE),
            Node(id="npc1", label="Dixie", kind=NodeKind.CONSTRUCT, zone=ZoneDepth.SURFACE),
            Node(id="data1", label="Data", kind=NodeKind.DATA, zone=ZoneDepth.SURFACE),
            Node(id="ice1", label="ICE", kind=NodeKind.ICE, zone=ZoneDepth.SURFACE, ice=IceKind.STANDARD),
        )
        return MatrixGraph(nodes=nodes, edges=(), entry_id="entry")

    def test_npc_at_construct_completes_meet_npc(self) -> None:
        """At NPC node during MEET_NPC stage → complete."""
        rs = RunState(current_stage=Stage.MEET_NPC)
        matrix = self._make_matrix()
        assert check_objective_at_node(rs, "npc1", matrix) is True

    def test_data_at_data_completes_extract(self) -> None:
        """At DATA node during EXTRACT_DATA stage → complete."""
        rs = RunState(current_stage=Stage.EXTRACT_DATA)
        matrix = self._make_matrix()
        assert check_objective_at_node(rs, "data1", matrix) is True

    def test_ice_at_ice_completes_defeat(self) -> None:
        """At ICE node during DEFEAT_ICE stage → complete (combat must also win)."""
        rs = RunState(current_stage=Stage.DEFEAT_ICE)
        matrix = self._make_matrix()
        # Note: arriving at ICE node is not the same as defeating it
        # — for now, just check arrival.
        assert check_objective_at_node(rs, "ice1", matrix) is True

    def test_wrong_node_does_not_complete(self) -> None:
        """At NPC node during EXTRACT_DATA stage → not complete."""
        rs = RunState(current_stage=Stage.EXTRACT_DATA)
        matrix = self._make_matrix()
        assert check_objective_at_node(rs, "npc1", matrix) is False

    def test_pending_stage_does_not_complete(self) -> None:
        """PENDING stage never completes via node visit."""
        rs = RunState(current_stage=Stage.PENDING)
        matrix = self._make_matrix()
        assert check_objective_at_node(rs, "npc1", matrix) is False

    def test_complete_stage_does_not_complete(self) -> None:
        """COMPLETE stage never completes via node visit."""
        rs = RunState(current_stage=Stage.COMPLETE)
        matrix = self._make_matrix()
        assert check_objective_at_node(rs, "npc1", matrix) is False

    def test_nonexistent_node(self) -> None:
        """Nonexistent node returns False (not crash)."""
        rs = RunState(current_stage=Stage.MEET_NPC)
        matrix = self._make_matrix()
        assert check_objective_at_node(rs, "nonexistent", matrix) is False

    def test_none_matrix(self) -> None:
        """None matrix returns False."""
        rs = RunState(current_stage=Stage.MEET_NPC)
        assert check_objective_at_node(rs, "npc1", None) is False


class TestCheckCombatVictory:
    """check_combat_victory() detects ICE stage completion."""

    def test_victory_during_ice_stage(self) -> None:
        """Combat victory during DEFEAT_ICE stage returns True."""
        rs = RunState(current_stage=Stage.DEFEAT_ICE)
        assert check_combat_victory(rs) is True

    def test_victory_during_wrong_stage(self) -> None:
        """Combat victory during wrong stage returns False."""
        for stage in (Stage.MEET_NPC, Stage.EXTRACT_DATA, Stage.COMPLETE, Stage.FAILED):
            rs = RunState(current_stage=stage)
            assert check_combat_victory(rs) is False


class TestCheckExtractComplete:
    """check_extract_complete() detects DATA stage completion."""

    def test_extract_during_data_stage(self) -> None:
        """Extract during EXTRACT_DATA stage returns True."""
        rs = RunState(current_stage=Stage.EXTRACT_DATA)
        assert check_extract_complete(rs) is True

    def test_extract_during_wrong_stage(self) -> None:
        """Extract during wrong stage returns False."""
        for stage in (Stage.MEET_NPC, Stage.DEFEAT_ICE, Stage.COMPLETE):
            rs = RunState(current_stage=stage)
            assert check_extract_complete(rs) is False


class TestCheckNpcTalkComplete:
    """check_npc_talk_complete() detects NPC stage completion."""

    def test_talk_during_npc_stage(self) -> None:
        """Talk during MEET_NPC stage returns True."""
        rs = RunState(current_stage=Stage.MEET_NPC)
        assert check_npc_talk_complete(rs) is True

    def test_talk_during_wrong_stage(self) -> None:
        """Talk during wrong stage returns False."""
        for stage in (Stage.EXTRACT_DATA, Stage.DEFEAT_ICE, Stage.COMPLETE):
            rs = RunState(current_stage=stage)
            assert check_npc_talk_complete(rs) is False

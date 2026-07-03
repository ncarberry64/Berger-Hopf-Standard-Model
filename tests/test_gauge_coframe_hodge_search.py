from bhsm.interface.gauge_coframe_hodge.source_search import search_gauge_coframe_hodge_sources
def test_search(): assert search_gauge_coframe_hodge_sources()["status"]=="SOURCE_SEARCH_COMPLETE_GAUGE_BASIS_OPEN_HODGE_CONDITIONAL"

import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import * as DocumentTitle from 'react-document-title';
import { RouteComponentProps } from 'react-router';
import { Search as UrlSearch } from 'history';

import LoadingSpinner from 'components/common/LoadingSpinner';
import ResourceList from 'components/common/ResourceList';
import ResourceSelector from './ResourceSelector';
import SearchPanel from './SearchPanel';

import { GlobalState } from 'ducks/rootReducer';
import { setPageIndex, setResource, urlDidUpdate } from 'ducks/search/reducer';
import {
  DashboardSearchResults,
  SearchResults,
  SetPageIndexRequest,
  SetResourceRequest,
  TableSearchResults,
  UrlDidUpdateRequest,
  UserSearchResults,
} from 'ducks/search/types';

import { Resource, ResourceType } from 'interfaces';
// TODO: Use css-modules instead of 'import'
import './styles.scss';

import {
  DOCUMENT_TITLE_SUFFIX,
  PAGE_INDEX_ERROR_MESSAGE,
  RESULTS_PER_PAGE,
  SEARCH_ERROR_MESSAGE_INFIX,
  SEARCH_ERROR_MESSAGE_PREFIX,
  SEARCH_ERROR_MESSAGE_SUFFIX,
  SEARCH_SOURCE_NAME,
  TABLE_RESOURCE_TITLE,
  USER_RESOURCE_TITLE,
} from './constants';


export interface StateFromProps {
  searchTerm: string;
  selectedTab: ResourceType;
  isLoading: boolean;
  tables: TableSearchResults;
  dashboards: DashboardSearchResults;
  users: UserSearchResults;
}

export interface DispatchFromProps {
  setResource: (resource: ResourceType) => SetResourceRequest;
  setPageIndex: (pageIndex: number) => SetPageIndexRequest;
  urlDidUpdate: (urlSearch: UrlSearch) => UrlDidUpdateRequest;
}

export type SearchPageProps = StateFromProps & DispatchFromProps & RouteComponentProps<any>;

export class SearchPage extends React.Component<SearchPageProps> {
  public static defaultProps: Partial<SearchPageProps> = {};

  constructor(props) {
    super(props);
  }

  componentDidMount() {
    this.props.urlDidUpdate(this.props.location.search);
  }

  componentDidUpdate(prevProps: SearchPageProps) {
    if (this.props.location.search !== prevProps.location.search) {
      this.props.urlDidUpdate(this.props.location.search);
    }
  }

  renderSearchResults = () => {
    switch(this.props.selectedTab) {
      case ResourceType.table:
        return this.getTabContent(this.props.tables, ResourceType.table);
      case ResourceType.user:
        return this.getTabContent(this.props.users, ResourceType.user);
      case ResourceType.dashboard:
        return this.getTabContent(this.props.dashboards, ResourceType.dashboard);
    }
    return null;
  };

  generateTabLabel = (tab: ResourceType): string => {
    switch (tab) {
      case ResourceType.table:
        return TABLE_RESOURCE_TITLE;
      case ResourceType.user:
        return USER_RESOURCE_TITLE;
      default:
        return '';
    }
  };

  getTabContent = (results: SearchResults<Resource>, tab: ResourceType) => {
    const { searchTerm } = this.props;
    const { page_index, total_results } = results;
    const startIndex = (RESULTS_PER_PAGE * page_index) + 1;
    const tabLabel = this.generateTabLabel(tab);

    // TODO - Move error messages into Tab Component
    // Check no results
    if (total_results === 0 && searchTerm.length > 0) {
      return (
        <div className="search-list-container">
          <div className="search-error body-placeholder">
            {SEARCH_ERROR_MESSAGE_PREFIX}<i>{ searchTerm }</i>{SEARCH_ERROR_MESSAGE_INFIX}{tabLabel.toLowerCase()}{SEARCH_ERROR_MESSAGE_SUFFIX}
          </div>
        </div>
      )
    }

    // Check page_index bounds
    if (page_index < 0 || startIndex > total_results) {
      return (
        <div className="search-list-container">
          <div className="search-error body-placeholder">
            {PAGE_INDEX_ERROR_MESSAGE}
          </div>
        </div>
      )
    }

    return (
      <div className="search-list-container">
        <ResourceList
          slicedItems={ results.results }
          slicedItemsCount={ total_results }
          source={ SEARCH_SOURCE_NAME }
          itemsPerPage={ RESULTS_PER_PAGE }
          activePage={ page_index }
          onPagination={ this.props.setPageIndex }
        />
      </div>
    );
  };

  renderContent = () => {
    if (this.props.isLoading) {
      return (<LoadingSpinner/>);
    }
    return this.renderSearchResults();
  };

  render() {
    const { searchTerm } = this.props;
    const innerContent = (
      <div className="search-page">
        <SearchPanel>
          <ResourceSelector/>
        </SearchPanel>
        <div className="search-results">
          { this.renderContent() }
        </div>
      </div>
    );
    if (searchTerm.length > 0) {
      return (
        <DocumentTitle title={ `${searchTerm}${DOCUMENT_TITLE_SUFFIX}` }>
          { innerContent }
        </DocumentTitle>
      );
    }
    return innerContent;
  }
}

export const mapStateToProps = (state: GlobalState) => {
  return {
    searchTerm: state.search.search_term,
    selectedTab: state.search.selectedTab,
    isLoading: state.search.isLoading,
    tables: state.search.tables,
    users: state.search.users,
    dashboards: state.search.dashboards,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ setResource, setPageIndex, urlDidUpdate }, dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(SearchPage);

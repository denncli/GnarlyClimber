
import React from 'react';
import PropTypes from 'prop-types';
import InfiniteScroll from 'react-infinite-scroll-component';

class Routes extends React.Component {
	constructor(props) {
    super(props);
    this.state = {
      height_sorted_routes: {},
      success : false,
      has_more : false,
      next_page_url : "",
      posts_urls : []
    };
    this.fetchTenMorePosts = this.fetchTenMorePosts.bind(this);
  }
  /*
  this setTimeout structure is taken from https://codesandbox.io/s/yk7637p62z,
  which is linked to as an example from https://www.npmjs.com/package/react-infinite-scroll-component,
  which is linked to from the spec
  */
  fetchTenMorePosts() {
    if(this.state.next_page_url == "") {
      this.setState({
        has_more: false
       });
    }
    else {
      setTimeout(() => {
        fetch(this.state.next_page_url, { credentials: 'same-origin' })
        .then((response) => {
            if (!response.ok) throw Error(response.statusText);
            return response.json(); //TODO: how to handle this error?
          })
          .then((data) => {
            this.setState(prevState => ({
              next_page_url: data.next,
              posts_urls: prevState.posts_urls.concat(data.results)
            }));
          })
          .catch((error) => console.log(error));
      }, 500);
      const state = { next_page_url: this.state.next_page_url,
        posts_urls: this.state.posts_urls };
      //history.replaceState(state, '', window.location.href);
      history.replaceState(state, '', '/');
    }
  }

	componentDidMount() {
    //warning: not compatible with opera or safari
    const NAVIGATION_BACK_FORWARD = 2;
    if(performance.navigation.type == NAVIGATION_BACK_FORWARD) {
      this.setState({
        next_page_url: history.state.next_page_url,
        posts_urls: history.state.posts_urls
      });
      return;
    }

    const { url } = this.props;
		fetch(url, { credentials: 'same-origin' })
		.then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          height_sorted_routes: data.height_sorted_routes,
          success: data.success
        });
      })
      .catch((error) => console.log(error));
  }

	render() {
    return (
      <p>this.state.height_sorted_routes</p>
      /*
      <InfiniteScroll
          dataLength={this.state.posts_urls.length} 
          next={this.fetchTenMorePosts}
          hasMore={this.state.has_more} 
          loader={<h4>Loading...</h4>}
          endMessage={
            <p style={{textAlign: 'center'}}>
              <b>Yay! You have seen it all</b>
            </p>
          }
      >
          {this.state.posts_urls.map(
            post => <Post url={post.url} key={post.postid}></Post>)}
      </InfiniteScroll>
      */
    );
	}
}

export default Feed
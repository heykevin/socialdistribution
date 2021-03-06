import _ from 'lodash';
import Reflux from 'reflux';

import { Request, apiPrefix } from '../utils/helpers';

import AuthorStore from './author';
import PostActions from '../actions/post';
import AuthorActions from '../actions/author';

import Post from '../objects/post';

// Deals with App State Machine state
export default Reflux.createStore({

  init: function() {

    this.pubPosts = [];
    this.timeline = [];

    // Listeners
    this.listenTo(PostActions.getTimeline, 'onGetTimeline');
    this.listenTo(PostActions.getPublicPosts, 'onGetPubPosts');

    // since creation of comments and posts is handling in the author store
    // we need to update posts/!app/ componenets when a state change occurs
    this.listenTo(AuthorActions.createPost.complete, 'onPostCreated');
    this.listenTo(AuthorActions.deletePost.complete, 'onPostDeleted');
    this.listenTo(AuthorActions.createComment.complete, 'onCommentCreated');

  },

  // fetches timelines posts
  onGetTimeline: function(token) {
    Request
      .get('/author/posts')
      .use(apiPrefix)
      .token(token)
      .promise(this.timelineComplete, PostActions.getTimeline.fail)
  },

  timelineComplete: function(postsData) {
    this.timeline = responseToPosts(postsData);

    this.trigger({timeline: this.timeline});
    PostActions.getTimeline.complete(this.timeline);
  },

  // fetches public posts
  onGetPubPosts: function () {
    Request
      .get('/posts')
      .use(apiPrefix)
      .promise(this.pubPostsComplete, PostActions.getPublicPosts.fail)
  },

  pubPostsComplete: function(postsData) {
    this.pubPosts = responseToPosts(postsData);

    this.trigger({publicPosts: this.pubPosts});
    PostActions.getPublicPosts.complete(this.pubPosts);
  },

  onPostCreated: function(post) {
    this.timeline.unshift(post);
    this.trigger({timeline: this.timeline});
  },

  onCommentCreated: function(comment) {
    this.triggerAll();
  },

  onPostDeleted: function(post) {
    _.pull(this.pubPosts, post);
    _.pull(this.timeline, post);

    this.triggerAll();
  },

  triggerAll: function() {
    this.trigger({timeline: this.timeline});
    this.trigger({publicPosts: this.pubPosts});
  }
});

function responseToPosts(postsData) {
  return _.sortByOrder(postsData.posts.map((post) => {
    return new Post(post);
  }), ['pubDate'], [false]);
}

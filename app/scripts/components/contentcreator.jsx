import _ from 'lodash';
import React from 'react';
import Reflux from 'reflux';
import { Link } from 'react-router';
import { addons } from 'react/addons';
import { Input } from 'react-bootstrap';
import { markdown as Markdown } from 'markdown';

import PostActions from '../actions/post';

// Responsible for creating posts/comments and notifying the Post store when
// this happens.
export default React.createClass({

  mixins: [addons.LinkedStateMixin],

  getInitialState: function() {
    return {
      format: "markdown",
      content: ""
    };
  },

  submitContent: function() {

    // capture the current content in our inputs
    var content = {
      author: this.props.currentAuthor,
      content: this.state.content,
      type: this.state.format
    };

    // reset content state now that we have it stored
    this.setState(this.getInitialState());

    // populate content with appropriate metadata
    if (this.props.forComment) {
      PostActions.newComment(this.props.post, content);
    } else {
      PostActions.newPost(content);
    }
  },

  render: function() {

    // don't go further if we don't have our current author prop
    if (_.isNull(this.props.currentAuthor)) {
      return (<div></div>);
    }

    var Submit = <Input className="pull-right" type="submit" value="Post" onClick={this.submitContent} />;
    return (
      <div className="media">
        <div className="media-left">
          <Link to="author" params={{id: this.props.currentAuthor.id}}>
            <img className="media-object author-image" src={this.props.currentAuthor.getImage()}/>
          </Link>
        </div>
        <div className="media-body content-creator">
          <Input type="textarea" placeholder="Say something witty..." valueLink={this.linkState('content')} />
          <Input type="select" valueLink={this.linkState('format')} buttonAfter={Submit}>
            <option value="markdown">Markdown</option>
            <option value="text">Text</option>
          </Input>
        </div>
      </div>
    );
  }
});

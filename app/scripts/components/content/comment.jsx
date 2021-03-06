import _ from 'lodash';
import React from 'react';
import Moment from 'moment';
import { Col } from 'react-bootstrap';

import Spinner from '../spinner';
import ProfileLink from './profile-link';

// Represents an individual comment
export default React.createClass({

  render: function() {
    if (_.isNull(this.props.data)) {
      return (<Spinner />);
    }

    return (
      <div className="media">
        <div className="media-left">
          <ProfileLink author={this.props.data.author}>
            <img className="media-object content-auth-img" src={this.props.data.author.image} />
          </ProfileLink>
        </div>
        <div className="media-body">
          <ProfileLink author={this.props.data.author}>
            <h4 className="media-heading">{this.props.data.author.name}</h4>
          </ProfileLink>
          {this.props.data.comment}
          <h6 className="light-text">{Moment(this.props.data.pubDate).fromNow()} by
            <ProfileLink author={this.props.data.author}>
              <span className="text-capitalize"> {this.props.data.author.displayname}</span>
            </ProfileLink>
            <span className="text-lowercase pull-right">{this.props.data.author.host}</span>
          </h6>
        </div>
      </div>
    );
  }
});

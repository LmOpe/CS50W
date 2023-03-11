document.addEventListener("DOMContentLoaded", () => {

    document.querySelector('#profile-page').style.display = 'none';
    /*==============================================================================================================
                                        Toggle the expanding bar on screen width change
    ===============================================================================================================*/
    document.querySelector('#show').onclick = () => {
        document.querySelector('.navbar-expand-lg').style.display = 'flex';
        document.querySelector('#show').style.display = 'none';
        document.querySelector('#hide').style.display = 'block';
    }

    document.querySelector('#hide').onclick = () => {
        document.querySelector('.navbar-expand-lg').style.display = 'none';
        document.querySelector('#show').style.display = 'unset';
        document.querySelector('#hide').style.display = 'none';
    }

    /*==============================================================================================================
                                         Add event listener for username
    ===============================================================================================================*/
    posters = document.querySelectorAll('.poster');
    for (let i = 0; i < posters.length; i++){
        posters[i].onclick = () => {
            profile(posters[i].innerHTML);
        }
    }

    /*==============================================================================================================
                        Show edit button on the posts by the current user, so that they can edit the post
    ===============================================================================================================*/
    document.querySelectorAll('.post').forEach((post) => {
        if(post.childElementCount == 6){
            post.children[0].onclick = () => {
                content = post.children[3].innerHTML;
                new_content = document.createElement('textarea');
                new_content.value = content;
                post.children[3].replaceWith(new_content);
                post.children[0].innerHTML = "Save";
                post.children[0].onclick = () => {
                    edit_post(new_content.value, content);
                }
            }
        }
    })

    /*==============================================================================================================
                        Enable user to click like button
    ===============================================================================================================*/
    like = document.querySelectorAll('.like').forEach((like) =>{
        like.onclick = () => {
        post_like(like.firstChild.innerHTML)
        }
    })
})


    /*====================================================================================
                                     Send new post to server
    ======================================================================================*/
function create_post(content) {
    fetch('/newpost', {
        method: 'POST',
        headers: {
            'X-CSRFTOKEN': getCookie("csrftoken")
        },
        body: JSON.stringify({
            content: content
        })
    })
        .then(response => response.json())
        .then(result => {

            // Respond with error or success
            error = result.error;
            success = result.message;
            if (success != null) {
                document.querySelector('#response').innerHTML = success;
            }
            else {
                document.querySelector('#response').innerHTML = error;
            }
            location.reload();
        });
}


/*====================================================================================
                      Function for getting the csrftoken
======================================================================================*/
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/*====================================================================================
                        Listen for click on a username
======================================================================================*/
function profile(poster) {
    fetch(`${poster}/profile`)
        .then(response => response.json())
        .then(result => {
            followings = result[2];
            followers = result[1];
            posts = result[0];
            console.log(result);
            document.querySelector('#user').innerHTML = posts[0].poster;
            if (document.querySelector('#user-name') != null && posts[0].poster == document.querySelector('#user-name').innerHTML) {
                document.querySelector('#fol').style.display = 'none';
            }
            document.querySelector('#followers').innerHTML = `${followers.length} Followers<br>`;
            document.querySelector('#followings').innerHTML = `${followings.length} Followings<br>`;
            document.querySelector('#user-posts').innerHTML = "Posts";
            followings.forEach((following) => {
                follow = document.createElement('p');
                follow.setAttribute('class', 'following');
                follow.innerHTML = following.following;
                document.querySelector('#followings').append(follow);
            })
            followers.forEach((follower) => {
                follows = document.createElement('p');
                follows.setAttribute('class', 'follower');
                follows.innerHTML = follower.follower;
                document.querySelector('#followers').append(follows);
            })
            posts.forEach((post) => {
                var postE = document.createElement('p');
                postE.setAttribute('class', 'post');
                postE.innerHTML = post.content;
                document.querySelector('#user-posts').append(postE);
            })


            document.querySelector('#posts-page').style.display = 'none';
            document.querySelector('#profile-page').style.display = 'block';

/*================================================================================================================================
                                 Display the follow button or the unfollow button if the user is signed in
==================================================================================================================================*/
            if (document.querySelector('#user-name') != null) {
                is_following = false;
                if (followers.length > 0) {
                    for (let i = 0; i < followers.length; i++) {
                        if (followers[i].follower == document.querySelector('#user-name').innerHTML) {
                            is_following = true;
                            document.querySelector('#follow').style.display = 'none';
                            document.querySelector('#unfollow').style.display = 'block';
                            return;
                        }
                        else {
                            document.querySelector('#unfollow').style.display = 'none';
                            document.querySelector('#follow').style.display = 'block';
                        }
                    }
                }
                else {
                    document.querySelector('#unfollow').style.display = 'none';
                    document.querySelector('#follow').style.display = 'block';
                }

            }
        })
}



document.addEventListener('DOMContentLoaded', () => {
/*====================================================================================
                         Listen for event on post form
======================================================================================*/
    document.querySelector("#post-form").onsubmit = () => {
        var content = document.querySelector("#content").value;
        create_post(content);
        return false;
    };

/*====================================================================================
                        Listen follow click event on follow
======================================================================================*/
    document.querySelector('#follow').onclick = () => {

        // Set the current user to be following whoseever profile page they are
        fetch(`/follow`, {
            method: 'PUT',
            body: JSON.stringify({
                follower: document.querySelector('#user-name').innerHTML,
                following: document.querySelector('#user').innerHTML,
                follow: true
            })
        })
            .then(response => response.json())
            .then(result => {
                console.log(result);
                profile(document.querySelector('#user').innerHTML);
                document.querySelector('#unfollow').style.display = 'block';
                document.querySelector('#follow').style.display = 'none';
            })
    }

    
    // Unfollow user on click of unfollow button
    document.querySelector('#unfollow').onclick = () => {

        // Set the current user to unfollow whoseever profile page they are
        fetch(`/follow`, {
            method: 'PUT',
            body: JSON.stringify({
                follower: document.querySelector('#user-name').innerHTML,
                following: document.querySelector('#user').innerHTML,
                follow: false
            })
        })
            .then(response => response.json())
            .then(result => {
                console.log(result);
                profile(document.querySelector('#user').innerHTML);
                document.querySelector('#unfollow').style.display = 'none';
                document.querySelector('#follow').style.display = 'block';
            })
    }
})

/*===================================================================================
                        Send request to server to like the post
=====================================================================================*/
function post_like(id){
    fetch('/like',{
        method: 'PUT',
        body: JSON.stringify({
            id: id,
            user: document.querySelector('#user-name').innerHTML,
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log(result);
        location.reload();
    })
}


/*===================================================================================
                        Edit the current user's post
=====================================================================================*/
function edit_post(content, previous_content){
    fetch(`/follow`, {
        method: 'PUT',
        body: JSON.stringify({
            content: content,
            previous_content: previous_content,
            edit: true
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log(result);
        location.reload();
    })
}
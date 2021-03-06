/********************************************************
 * Copyright (c) 2013 Azavea, Inc.
 * See LICENSE in the project root for copying permission
 * JavaScript for the starred locations page 
 ********************************************************/

define(['jquery', 'Leaflet', 'text!templates/location.html', 'common', 'favorites', 'Handlebars'], 
    function($, L, html, common, favorites, Handlebars) {
        'use strict';

        $(document).ready(function() {
            // Draw the Handlebars template for a location 
            function drawStarredLocations(data) {
                var template = Handlebars.compile(html),
                    container = $('.container'),
                    $starred = $('<div></div>'),
                    numLocations = data.locations.length,
                    divRowHtml = '<div class="row bm20"></div>',
                    $divRow = $(divRowHtml);

                for (var i = 0; i < numLocations; i++) {
                    var loc = data.locations[i];
                    var $location = $(template(loc)).addClass("span4");
                    $divRow.append($location);

                    if ((i + 1) % 3 === 0 || i === numLocations - 1) {
                        $starred.append($divRow);
                        $divRow = $(divRowHtml);
                    }
                }

                // attach in single dom operation
                container.html($starred);     

                // Remove map and share button for each location
                $('.fav-count').html(numLocations);

                
                // add close buttons and click listener if we are displaying cookie locations
                //      else hide because this was a shared link and the "remove" functionality
                //      does not make sense
                if (!regexResult) {
                    $('.favs-close-button').removeClass('none').on('click', function(e) {
                        var $favorite = $(this).parent(),
                            key = $favorite.data('key');
    
                        favorites.removeIdFromCookie(key);
                        $.getJSON(common.getUrl('location-api', { locations: favorites.getCookie() }), drawStarredLocations);
                    });
                }
            }

            // get location ids:
            // url --> string :: /starred/12,13,54/  --> "12,13,54" 
            //      -- or --
            // cookie string 
            var cookie = favorites.getCookie(),
                regexResult = /([0-9,]+)/.exec(window.location.pathname),
                starredIds = "";

            if (regexResult || cookie) {
                starredIds = regexResult ? regexResult[1] : cookie;
                $.getJSON(common.getUrl('location-api', { locations: starredIds }), drawStarredLocations);
            } else {
                $('.container').html(gettext('No Favorite Locations'));
            }

            favorites.addClearListener();
            favorites.addShareListener();
        });
    }
);


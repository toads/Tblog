var imgObj;
for( i = 0; i < document.getElementsByTagName("img").length; i++ ){
    imgObj = document.getElementsByTagName("img")[i];
    if ( imgObj.width > 500 ) {
        imgObj.width = 500
    }
    if ( imgObj.height > 700 ){
    imgObj.height = 700
    }
    // imgObj.style['margin-right']="auto";
}

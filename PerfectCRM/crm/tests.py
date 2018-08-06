from django.test import TestCase

# Create your tests here.
"""
<script>
    Dropzone.options.myAwesomeDropzone = false;

    $("#myAwesomeDropzone").dropzone({
        {#url: "handle-upload.php",#}
        dictDefaultMessage:"点击或拖拽文件至此，可添加文件",
        {#dictInvalidInputType:"必须是'.txt'结尾的文件",#}
        dictFileTooBig:"文件过大，必须 <= 3M",
        dictRemoveFile:"remove file",
        addRemoveLinks: true,
        dictRemoveLinks: "x",
        dictCancelUpload: "x",
        maxFiles: 3,
        maxFilesize: 1,
        acceptedFiles: '.jpg,.jpeg,.png',
        init: function() {

            this.on("success", function(file,response) {
                var response = JSON.parse(response);
                if (!response.status) {
                    alert(response.err_msg);
                } else {
                    $("#uploaded_files").append("<li>" + file.name + "</li>");

                }
            });

            this.on("removedfile", function(file) {
                $.ajax({
                    type: 'POST',
                    url: '{% url 'enrollment_fileupload' enrollment_obj.id %}',
                    data: { 'path': file.path }
                });
                console.log("123");
                {#$("#uploaded_files").remove($.parseHTML('"<li>" + file.name + "</li>"'));#}

            });
        }
    });

    </script>

"""
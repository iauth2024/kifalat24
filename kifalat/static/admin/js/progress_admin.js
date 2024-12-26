(function($) {
    $(document).ready(function() {
        // Listen for changes in the Kafeel dropdown
        $('#id_kafeel').on('change', function() {
            var kafeelId = $(this).val();

            // Send an AJAX request to fetch the students for the selected Kafeel
            $.ajax({
                url: '/admin/get_students/',
                data: {'kafeel_id': kafeelId},
                dataType: 'json',
                success: function(data) {
                    var studentSelect = $('#id_student');
                    // Clear existing options
                    studentSelect.empty();

                    // Populate the students dropdown with the received data
                    $.each(data.students, function(index, student) {
                        var option = $('<option>').val(student.id).text(student.name);
                        studentSelect.append(option);
                    });
                },
                error: function(xhr, status, error) {
                    console.error('Error fetching students:', status, error);
                }
            });
        });
    });
})(django.jQuery);

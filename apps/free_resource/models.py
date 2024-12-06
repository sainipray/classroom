from django.db import models
from django_extensions.db.models import TimeStampedModel


class FreeResource(TimeStampedModel):
    title = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def content(self):
        # Define the file extensions for videos and images
        VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}
        IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

        # Initialize counts
        counts = {
            'videos': 0,
            'images': 0,
            'total_files': 0
        }

        def fetch_folder_structure(folder):
            nonlocal counts  # Allows access to the counts dictionary defined in the outer scope

            folder_data = {
                'id': folder.id,
                'title': folder.title,
                'order': folder.order,
                'files': [],
                'subfolders': []
            }
            # Fetch files within the folder
            for file in folder.files.all():
                # Determine the file extension
                extension = file.url.name.rsplit('.', 1)[-1].lower()

                # Increment counts based on file type
                if extension in VIDEO_EXTENSIONS:
                    counts['videos'] += 1
                elif extension in IMAGE_EXTENSIONS:
                    counts['images'] += 1

                counts['total_files'] += 1

                # TODO we don't need to show urls of each file that is locked or if student not purchased course
                # Append file data
                folder_data['files'].append({
                    'id': file.id,
                    'title': file.title,
                    'url': file.url.url,  # URL to access the file
                    'is_locked': file.is_locked,
                    'order': file.order
                })

            # Recursively fetch subfolders
            for subfolder in folder.folders.all().order_by('order'):
                folder_data['subfolders'].append(fetch_folder_structure(subfolder))

            return folder_data

        folder_structure = []
        # Start from top-level folders (where parent is None)
        for folder in self.folders.filter(parent__isnull=True).order_by('order'):
            folder_structure.append(fetch_folder_structure(folder))

        # Prepare the final data with directory structure and counts
        data = {
            'directory': folder_structure,
            'videos': counts['videos'],
            'images': counts['images'],
            'total_files': counts['total_files']
        }

        return data


class Folder(TimeStampedModel):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='folders')
    resource = models.ForeignKey(FreeResource, related_name="folders", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name="Folder Title")
    order = models.PositiveIntegerField(default=0, verbose_name="Order")  # Field to handle the order

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('order', '-created')


class File(TimeStampedModel):
    folder = models.ForeignKey(Folder, related_name="files", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name="Lecture Title")
    url = models.FileField(upload_to='videos/', verbose_name="Lecture Video")
    is_locked = models.BooleanField(default=False, verbose_name="Is Locked")
    order = models.PositiveIntegerField(default=0, verbose_name="Order")  # Field to handle the order

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('order', '-created')

    def save(self, **kwargs):
        # Automatically set the title from the document file name, if title is empty
        if not self.title and self.url:
            self.title = self.url.name.rsplit('/', 1)[-1]  # Get the file name only
        super(File, self).save(**kwargs)

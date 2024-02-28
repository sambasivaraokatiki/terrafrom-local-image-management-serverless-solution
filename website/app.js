const express = require('express');
const bodyParser = require('body-parser');
const multer = require('multer');
const fs = require('fs');
const request = require('request');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static('public'));
app.use(bodyParser.urlencoded({ extended: true }));

const upload = multer({ dest: 'uploads/' });

// Render the index.html page
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

serverURI='http://4huaiqt1uz.execute-api.localhost.localstack.cloud:4566/dev'
// Handle image upload
app.post('/upload', upload.single('file'), (req, res) => {
    // Send the file to the backend server
    const backendUrl = serverURI+'/upload';
    const formData = {
        file: fs.createReadStream(req.file.path)
    };
    request.post({ url: backendUrl, formData: formData }, (err, response, body) => {
        console.log(body);
        if (err) {
            console.error('Error uploading file:', err);
            res.status(500).send('Error uploading file');
        } else {
            // Delete temporary file after upload
            fs.unlink(req.file.path, (err) => {
                if (err) {
                    console.error('Error deleting file:', err);
                }
            });
            res.status(200).send('File uploaded successfully');
        }
    });
});

// Handle image list
app.get('/list', (req, res) => {
    const backendUrl=serverURI+'/list_search';
    request.post(backendUrl).pipe(res);
});

// Handle image search
app.post('/search', (req, res) => {
    const searchOption = req.body.search_option;
    const searchTerm = req.body.search_term.toLowerCase();
    const backendUrl=serverURI+'/list_search';
    const jsonData = {
        name: searchOption,
        value: searchTerm
    };
    const options = {
        url: backendUrl,
        method: 'POST',
        json: true,
        body: jsonData
    };
    request(options).pipe(res);
});

// Handle image view
app.get('/view/:imageName', (req, res) => {
    const imageName = req.params.imageName;
    const backendUrl = serverURI+`/view-download/view/${imageName}`;
    
    request.get(backendUrl, (error, response, body) => {
        if (error) {
            console.error('Error:', error);
            res.status(500).send('Error fetching image');
            return;
        }
        
        if (response.statusCode === 200) {
            const imageDataURI = `data:${response.headers['content-type']};base64,${body.toString('base64')}`;
            res.json({imageDataURI});
        } else {
            console.error('Error: Invalid image response');
            res.status(500).send('Invalid image response');
        }
    });
});

// Handle image download
app.get('/download/:imageName', (req, res) => {
    const imageName = req.params.imageName;
    const backendUrl = serverURI+`/view-download/download/${imageName}`;
    request.get(backendUrl)
        .on('error', (err) => {
            console.error('Error:', err);
        })
        .pipe(fs.createWriteStream(`downloads/${imageName}`))
        .on('finish', () => {
            console.log('Image downloaded successfully');
        });
});

// Handle image delete
app.get('/delete/:imageName', (req, res) => {
    const imageName = req.params.imageName;
    const backendUrl = serverURI+`/delete/${imageName}`;
    request.get(backendUrl).pipe(res);
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});

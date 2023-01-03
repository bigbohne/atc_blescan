<html>
<head>
  <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/semantic-ui@2.4.2/dist/semantic.min.css">
  <script
    src="https://code.jquery.com/jquery-3.1.1.min.js"
    integrity="sha256-hVVnYaiADRTO2PzUGmuLJr8BLUSjGIZsDYGmIJLv2b8="
    crossorigin="anonymous"></script>
  <script src="https://cdn.jsdelivr.net/npm/semantic-ui@2.4.2/dist/semantic.min.js"></script>
  <title>Sensoren</title>
  <meta http-equiv="refresh" content="30">
</head>
<body>
  <div class="ui main text container">
  <h1>Aktuelle Messwerte:</h1>
  <table class="ui celled table">
    <thead>
      <tr>
        <th>Sensor</th>
        <th>Temperatur</th>
        <th>Feuchtigkeit</th>
        <th>Batterie</th>
      </tr>
    </thead>
    <tbody>
    % for sensor in sensors:
    <tr>
      <td>{{sensor['name']}}</td>
      <td><b>{{sensor['temp']}}&deg;C</b></td>
      <td>{{sensor['humi']}}%</td>
      <td>{{sensor['bat_perc']}}%</td>
    </tr>
    % end
    </tbody>
  </table>  
  </div>
</body>
</html>

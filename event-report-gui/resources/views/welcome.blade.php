@extends('master')

@section('body')

    <div id="map">
    </div>

    <div style="display: none;">
        <table id="rekap" class="table table-striped table-bordered" style="width:100%">
            <thead>
                <tr>    
                    <th>ID</th>
                    <th>User ID</th>
                    <th>Tweet</th>
                    <th>Created at</th>
                    <th>Place</th>
                    <th>Address</th>
                    <th>Latitude</th>
                    <th>Longitude</th>
                </tr>
            </thead>
            <tbody>
                @foreach ($tweets as $tweet)
                <tr>
                    <td>{{ $tweet->id }}</td>
                    <td>{{ $tweet->user_id }}</td>
                    <td>{{ $tweet->tweet }}</td>
                    <td>{{ $tweet->created_at }}</td>
                    <td>{{ $tweet->place }}</td>
                    <td>{{ $tweet->address }}</td>
                    <td>{{ $tweet->latitude }}</td>
                    <td>{{ $tweet->longitude }}</td>
                </tr>
                @endforeach
                
            </tbody>
        </table>
    </div>

    
@endsection

@section('js')
    <script src="https://maps.googleapis.com/maps/api/js?key={{ env('MAP_API_KEY') }}&callback=initMap&libraries=places" 
    async defer></script>

    <script>
        $(document).ready(function(){
            $(".navbar .navbar-nav .nav-item:nth-child(1)").addClass("active");
        });
    </script>
@endsection
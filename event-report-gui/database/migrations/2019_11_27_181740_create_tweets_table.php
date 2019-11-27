<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateTweetsTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('tweet', function (Blueprint $table) {
            $table->bigIncrements('id');
            $table->string('tweet_id', 50)->nullable();
            $table->string('user_id', 50)->nullable();
            $table->text('tweet')->nullable();
            $table->timestamps();
            
            $table->string('place', 150)->nullable();
            $table->string('address', 250)->nullable();
            $table->float('latitude', 10, 7)->nullable();
            $table->float('longitude', 10, 7)->nullable();
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('tweet');
    }
}

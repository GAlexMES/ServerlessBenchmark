plugins {
    java
}

repositories {
    mavenCentral()
}

java.sourceCompatibility = JavaVersion.VERSION_11
java.targetCompatibility = JavaVersion.VERSION_11

dependencies {
    implementation("com.amazonaws:aws-lambda-java-core:1.1.0")
    implementation("com.amazonaws:aws-lambda-java-log4j:1.0.0")
    implementation("com.fasterxml.jackson.core:jackson-core:2.8.5")
    implementation("com.fasterxml.jackson.core:jackson-databind:2.8.5")
    implementation("com.fasterxml.jackson.core:jackson-annotations:2.8.5")
}

tasks.register<Zip>("packageDistribution") {
    archiveFileName.set("hello.zip")
    destinationDirectory.set(layout.buildDirectory.dir("dist"))

    from(tasks.compileJava)
    from(tasks.processResources)
}


// Task for building the zip file for upload
//tasks.buildZip(type: Zip) {
//    baseName = "hello"
//    from compileJava
//    from processResources
//    into('lib') {
//        from configurations.runtime
//    }
//}

tasks["build"].dependsOn("packageDistribution")


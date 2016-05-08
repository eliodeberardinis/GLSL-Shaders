#include "ShaderTester.h"

const int WINDOW_WIDTH = 1024;
const int WINDOW_HEIGHT = 768;

SDL_Window *window;
bool running;

// Time in seconds since SDL init
float globalTime;
// Time since last frame
float deltaTime;

GLuint vao, vbo;

shader_test::ShaderLoader *shaderLoader;
GLuint currentShaderProgram;

void init(int width, int height) {
    running = true;

    SDL_Init(SDL_INIT_EVERYTHING);

    window = SDL_CreateWindow("Shader Test", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height, SDL_WINDOW_OPENGL);
    if (window == nullptr) {
        printf("ERR: SDL_Window failed to initialize.\n");
        SDL_Quit();
        exit(1);
    }

    SDL_GLContext gl_context = SDL_GL_CreateContext(window);
    if (gl_context == nullptr) {
        printf("ERR: SDL_GLContext failed to initialize.\n");
        SDL_Quit();
        exit(1);
    }

    if (glewInit() != GLEW_OK) {
        printf("ERR: GLEW failed to initialize.\n");
        SDL_Quit();
        exit(1);
    }

    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);

    glEnable(GL_DEPTH_TEST);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
}

void create_geometry() {
    std::vector<shader_test::Vertex> vertices = std::vector<shader_test::Vertex>(4);

    vertices.clear();
    vertices.push_back(shader_test::Vec3(-1.0f, 1.0f, 0.0f));
    vertices.push_back(shader_test::Vec3(1.0f, 1.0f, 0.0f));
    vertices.push_back(shader_test::Vec3(-1.0f, -1.0f, 0.0f));
    vertices.push_back(shader_test::Vec3(1.0f, -1.0f, 0.0f));

    glGenVertexArrays(1, &vao);
    glBindVertexArray(vao);

    glGenBuffers(1, &vbo);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(shader_test::Vertex) * vertices.size(), &vertices[0], GL_STATIC_DRAW);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(shader_test::Vertex), (void*)0);

    glBindVertexArray(0);
}

void load_shader(char *vsPath, char *fsPath) {
    shaderLoader = new shader_test::ShaderLoader();
    currentShaderProgram = shaderLoader->CreateProgram(vsPath, fsPath);
}

void compute_time() {
    Uint32 now = SDL_GetTicks();
    static Uint32 last = 0;

    if (now > last) {
        globalTime = (float)now / 1000.0f;
        deltaTime = (float)(now - last) / 1000.0f;

        last = now;
    }
}

void handle_input() {
    SDL_Event evnt;

    while (SDL_PollEvent(&evnt)) {
        switch (evnt.type) {
            case SDL_QUIT:
                running = false;
                break;
            default:
                break;
        }
    }
}

void draw() {
    glClearDepth(1.0f);
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    glUseProgram(currentShaderProgram);

    float resolution[] = { (float)WINDOW_WIDTH, (float)WINDOW_HEIGHT };
    GLuint resLocation = glGetUniformLocation(currentShaderProgram, "resolution");
    glUniform2fv(resLocation, 1, resolution);

    GLuint globalTimeLocation = glGetUniformLocation(currentShaderProgram, "globalTime");
    glUniform1f(globalTimeLocation, globalTime);

    glBindVertexArray(vao);
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
    glBindVertexArray(0);

    SDL_GL_SwapWindow(window);
}

void loop() {
    while (running) {
        compute_time();
        handle_input();
        draw();
    }
}

void cleanup() {
    SDL_Quit();
    delete shaderLoader;
}

int main(int argc, char **argv) {

    // Init SDL and OpenGL
    init(WINDOW_WIDTH, WINDOW_HEIGHT);

    // Create NDC quad
    create_geometry();

    // Select desired shader
    char *vertexShaderPath = "Shaders\\DefaultVS.glsl";
    char *fragmentShaderPath = "Shaders\\SphereFS.glsl";
    load_shader(vertexShaderPath, fragmentShaderPath);

    // Main rendering loop
    loop();

    // Remove references
    cleanup();

    return 0;
}
